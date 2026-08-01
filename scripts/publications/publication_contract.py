# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Contrato deterministico compartilhado pela cadeia de publicacoes.

Centraliza identidade editorial, paths, hashes, assinaturas, colisoes e
metadados. A unidade nao acessa rede nem produz efeitos durante importacao.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
import unicodedata
from urllib.parse import urlsplit
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPOSITORY_ROOT / "config" / "publications.json"
SOURCE_SCHEMA = "egw-source/v2"
SOURCE_SCHEMA_V3 = "publication-source/v3"
FORMAT_ORDER = {"pdf": 0, "epub": 1}
WINDOWS_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LANGUAGE_RE = re.compile(r"^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$")
URI_SLUG_MAX_BYTES = 180
URI_TRANSLITERATION = str.maketrans(
    {
        "æ": "ae",
        "ð": "d",
        "đ": "d",
        "ı": "i",
        "ł": "l",
        "ø": "o",
        "œ": "oe",
        "þ": "th",
    }
)


class ContractError(ValueError):
    """Sinaliza violacao deterministica do contrato de publicacoes."""


@dataclass(frozen=True)
class FileHashes:
    """Hashes integrais calculados na mesma passagem binaria."""

    sha1: str
    sha256: str
    sha512: str
    size: int

    def as_dict(self) -> dict[str, str]:
        return {
            "sha1": self.sha1,
            "sha256": self.sha256,
            "sha512": self.sha512,
        }


@dataclass(frozen=True)
class PublicationIdentity:
    """Identidade e destino canônico de um grupo editorial."""

    author: str
    language: str
    publication_type: str
    title: str
    acronym: str
    route_slug: str

    def relative_directory(self) -> Path:
        return Path(
            self.author,
            self.language,
            self.publication_type,
            self.route_slug,
        )

    def asset_name(self, publication_format: str, qualifier: str | None = None) -> str:
        validate_format(publication_format)
        middle = f".{qualifier}" if qualifier else ""
        return f"{self.acronym}{middle}.{publication_format}"

    def metadata_name(self) -> str:
        return f"{self.acronym}.source.json"


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict:
    """Carrega configuracao fechada e resolve somente paths declarados."""

    config_path = Path(path).resolve()
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"configuracao invalida: {config_path}: {error}") from error
    schema = data.get("schema_version")
    required_v1 = {"schema_version", "source_root", "public_root", "authors", "download"}
    required_v2 = {
        "schema_version",
        "source_root",
        "public_root",
        "state_root",
        "authors",
        "collections",
        "download",
    }
    required_v3 = {
        "schema_version",
        "source_root",
        "public_root",
        "runtime_state_root",
        "authors",
        "collections",
        "download",
        "transaction",
    }
    if schema == 1 and set(data) != required_v1:
        raise ContractError("configuracao deve seguir publications-config/v1")
    if schema == 2 and set(data) != required_v2:
        raise ContractError("configuracao deve seguir publications-config/v2")
    if schema == 3 and set(data) != required_v3:
        raise ContractError("configuracao deve seguir publications-config/v3")
    if schema not in {1, 2, 3}:
        raise ContractError("schema de configuracao nao suportado")
    if not isinstance(data["authors"], dict) or not data["authors"]:
        raise ContractError("configuracao sem autores")
    if schema in {2, 3}:
        if not isinstance(data["collections"], list) or not data["collections"]:
            raise ContractError("configuracao sem colecoes")
        ids = [item.get("id") for item in data["collections"] if isinstance(item, dict)]
        if len(ids) != len(data["collections"]) or len(ids) != len(set(ids)):
            raise ContractError("colecoes invalidas ou duplicadas")
    if schema == 3:
        transaction = data["transaction"]
        if not isinstance(transaction, dict) or set(transaction) != {
            "branch",
            "commit_per_publication",
        }:
            raise ContractError("transacao Git invalida")
        if transaction["branch"] != "dev" or not isinstance(
            transaction["commit_per_publication"], bool
        ):
            raise ContractError("politica Git exige branch dev e opt-in booleano")
    return data


def runtime_paths(config: dict, repository_root: Path = REPOSITORY_ROOT) -> dict[str, Path]:
    """Resolve toda escrita local mutavel a partir de uma única raiz."""

    root_value = config.get(
        "runtime_state_root",
        config.get("state_root", "constructor/.state/egwsearch"),
    )
    root = resolve_repository_path(str(root_value), repository_root)
    browser_name = str(
        config.get("download", {}).get("browser_profile_name", "egwwritings")
    )
    validate_slug(browser_name, "perfil de navegador")
    paths = {
        "root": root,
        "acquisition": root / "acquisition",
        "browser_profile": root / "profiles" / browser_name,
        "python_environment": root / "environments" / "python",
        "downloads": root / "tmp" / "downloads",
        "locks": root / "locks",
        "logs": root / "logs",
    }
    resolved_root = root.resolve()
    for label, value in paths.items():
        resolved = value.resolve()
        if label != "root" and resolved_root not in resolved.parents:
            raise ContractError(f"path de runtime fora da raiz: {label}")
    return paths


def resolve_repository_path(value: str, repository_root: Path = REPOSITORY_ROOT) -> Path:
    """Resolve path relativo e bloqueia escape da raiz do repositorio."""

    candidate = (repository_root / value).resolve()
    root = repository_root.resolve()
    if candidate != root and root not in candidate.parents:
        raise ContractError(f"path fora da raiz: {value}")
    return candidate


def normalize_editorial_title(title: str) -> str:
    """Preserva o titulo editorial e remove somente ruido estrutural."""

    if not isinstance(title, str):
        raise ContractError("titulo deve ser string")
    normalized = unicodedata.normalize("NFC", title)
    normalized = "".join(
        " " if unicodedata.category(character).startswith("C") else character
        for character in normalized
    )
    normalized = " ".join(normalized.split())
    if not normalized:
        raise ContractError("titulo vazio")
    return normalized


def uri_slug(value: str) -> str:
    """Projeta titulo editorial em segmento URI ASCII estavel.

    A projecao e usada somente por diretorios e rotas: o titulo original
    continua sendo a autoridade editorial. A normalizacao remove marcas e
    pontuacao, preserva fronteiras de espaco como hifen e limita o segmento
    para manter portabilidade entre Windows, Git e hospedagem estatica.
    """

    normalized = normalize_editorial_title(value)
    folded = unicodedata.normalize("NFKC", normalized).casefold()
    folded = folded.translate(URI_TRANSLITERATION)
    decomposed = unicodedata.normalize("NFKD", folded)
    without_marks = "".join(
        character
        for character in decomposed
        if not unicodedata.category(character).startswith("M")
    )
    spaced = re.sub(r"\s+", "-", without_marks)
    ascii_only = spaced.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9-]", "", ascii_only)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
        slug = f"u-{digest}"
    if slug in WINDOWS_RESERVED:
        slug = f"u-{slug}"
    if len(slug.encode("ascii")) > URI_SLUG_MAX_BYTES:
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
        prefix_length = URI_SLUG_MAX_BYTES - len(digest) - 1
        prefix = slug[:prefix_length].rstrip("-")
        slug = f"{prefix}-{digest}"
    if not SLUG_RE.fullmatch(slug):
        raise ContractError(f"slug URI invalido: {slug!r}")
    return slug


def _ascii_token(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(
        character.lower()
        for character in decomposed
        if character.isascii() and character.isalnum()
    )


def title_acronym(title: str) -> str:
    """Deriva identificador curto exclusivamente do titulo normalizado."""

    normalized = normalize_editorial_title(title)
    tokens = re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)
    ascii_tokens = [token for token in (_ascii_token(item) for item in tokens) if token]
    if len(ascii_tokens) == 1:
        acronym = ascii_tokens[0][:24]
    else:
        acronym = "".join(token[0] for token in ascii_tokens)[:24]
    if not acronym:
        acronym = f"u{hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:12]}"
    return acronym


def validate_slug(value: str, label: str) -> str:
    if not isinstance(value, str) or not SLUG_RE.fullmatch(value):
        raise ContractError(f"{label} invalido: {value!r}")
    return value


def validate_language(value: str) -> str:
    if not isinstance(value, str) or value != value.lower() or not LANGUAGE_RE.fullmatch(value):
        raise ContractError(f"idioma BCP 47 invalido: {value!r}")
    return value


def publication_identity(
    author: str,
    language: str,
    publication_type: str,
    title: str,
) -> PublicationIdentity:
    """Materializa identidade somente depois de validar seus componentes."""

    normalized_title = normalize_editorial_title(title)
    return PublicationIdentity(
        author=validate_slug(author, "autor"),
        language=validate_language(language),
        publication_type=validate_slug(publication_type, "tipo"),
        title=normalized_title,
        acronym=title_acronym(normalized_title),
        route_slug=uri_slug(normalized_title),
    )


def validate_format(value: str) -> str:
    if value not in FORMAT_ORDER:
        raise ContractError(f"formato invalido: {value!r}")
    return value


def format_from_url(url: str) -> str:
    path = urlsplit(url).path.casefold()
    for publication_format in FORMAT_ORDER:
        if path.endswith(f".{publication_format}"):
            return publication_format
    raise ContractError(f"URL sem formato PDF/EPUB: {url}")


def validate_source_url(
    url: str,
    allowed_hosts: set[str] | None = None,
    https_only: bool = True,
) -> str:
    """Valida sintaxe e autoridade antes de qualquer acesso de rede."""

    if not isinstance(url, str) or not url:
        raise ContractError("URL deve ser string nao vazia")
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError) as error:
        raise ContractError(f"URL invalida: {url!r}") from error
    allowed_schemes = {"https"} if https_only else {"http", "https"}
    if parsed.scheme.lower() not in allowed_schemes:
        raise ContractError(f"esquema de URL nao permitido: {parsed.scheme!r}")
    if not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ContractError("URL exige host e proibe credencial/fragmento")
    host = parsed.hostname.casefold().rstrip(".")
    if allowed_hosts is not None and host not in {item.casefold() for item in allowed_hosts}:
        raise ContractError(f"host nao permitido: {host}")
    format_from_url(url)
    return url


def hash_file(path: Path | str, chunk_size: int = 1024 * 1024) -> FileHashes:
    """Calcula os tres hashes sobre os mesmos chunks binarios integrais."""

    if chunk_size <= 0:
        raise ContractError("chunk_size deve ser positivo")
    algorithms = {
        "sha1": hashlib.sha1(usedforsecurity=False),
        "sha256": hashlib.sha256(),
        "sha512": hashlib.sha512(),
    }
    size = 0
    with Path(path).open("rb") as stream:
        while chunk := stream.read(chunk_size):
            size += len(chunk)
            for algorithm in algorithms.values():
                algorithm.update(chunk)
    return FileHashes(
        sha1=algorithms["sha1"].hexdigest(),
        sha256=algorithms["sha256"].hexdigest(),
        sha512=algorithms["sha512"].hexdigest(),
        size=size,
    )


def validate_file_signature(path: Path | str, publication_format: str) -> None:
    """Confirma assinatura minima e estrutura do contêiner recebido."""

    validate_format(publication_format)
    candidate = Path(path)
    if publication_format == "pdf":
        with candidate.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                raise ContractError(f"assinatura PDF invalida: {candidate}")
        return
    if not zipfile.is_zipfile(candidate):
        raise ContractError(f"EPUB nao e ZIP OCF: {candidate}")
    try:
        with zipfile.ZipFile(candidate) as archive:
            info = archive.getinfo("mimetype")
            if info.file_size > 128:
                raise ContractError("mimetype EPUB excede limite")
            value = archive.read(info)
    except (KeyError, OSError, zipfile.BadZipFile) as error:
        raise ContractError(f"estrutura EPUB invalida: {candidate}") from error
    if value != b"application/epub+zip":
        raise ContractError(f"mimetype EPUB invalido: {candidate}")


def choose_variant_path(base_path: Path, sha256: str) -> tuple[Path, bool]:
    """Seleciona destino sem sobrescrever variante material.

    Retorna ``(path, duplicate)``. ``duplicate`` indica que o destino
    selecionado ja contem exatamente os mesmos bytes.
    """

    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ContractError("SHA-256 invalido")
    if not base_path.exists():
        return base_path, False
    if hash_file(base_path).sha256 == sha256:
        return base_path, True
    suffix = "".join(base_path.suffixes)
    stem = base_path.name[: -len(suffix)] if suffix else base_path.name
    for length in range(8, 65, 2):
        candidate = base_path.with_name(f"{stem}.{sha256[:length]}{suffix}")
        if not candidate.exists():
            return candidate, False
        if hash_file(candidate).sha256 == sha256:
            return candidate, True
    raise ContractError(f"colisao SHA-256 integral: {base_path}")


def read_source_records(path: Path | str) -> list[dict]:
    """Le metadado v2 ou legado URL-chaveado sem descartar evidencia."""

    metadata_path = Path(path)
    try:
        data = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"metadado invalido: {metadata_path}: {error}") from error
    if isinstance(data, dict) and data.get("schema_version") in {
        SOURCE_SCHEMA,
        SOURCE_SCHEMA_V3,
    }:
        if data["schema_version"] == SOURCE_SCHEMA_V3:
            required_v3 = {
                "schema_version",
                "identity",
                "collection",
                "state",
                "sources",
                "segments",
                "derivations",
                "history",
            }
            if set(data) != required_v3:
                raise ContractError(f"metadado v3 com raiz divergente: {metadata_path}")
            if not isinstance(data["sources"], list):
                raise ContractError(f"sources invalido: {metadata_path}")
            return list(data["sources"])
        if set(data) != {"schema_version", "identity", "sources"}:
            raise ContractError(f"metadado v2 com raiz divergente: {metadata_path}")
        if not isinstance(data["sources"], list):
            raise ContractError(f"sources invalido: {metadata_path}")
        return list(data["sources"])
    if not isinstance(data, dict):
        raise ContractError(f"metadado legado deve ser objeto: {metadata_path}")
    records = []
    for url, details in data.items():
        if not isinstance(url, str) or not isinstance(details, dict):
            raise ContractError(f"entrada legada invalida: {metadata_path}")
        publication_format = format_from_url(url)
        records.append(
            {
                "format": publication_format,
                "url": url,
                "accessed_at": details.get("acesso"),
                "size": details.get("size"),
                "hashes": {
                    "sha1": details.get("sha1"),
                    "sha256": details.get("sha256"),
                    "sha512": details.get("sha512"),
                },
            }
        )
    return sorted(records, key=source_record_sort_key)


def source_record_sort_key(record: dict) -> tuple[int, str]:
    return FORMAT_ORDER.get(record.get("format"), 99), str(record.get("url", ""))


def build_source_document(
    identity: PublicationIdentity,
    records: list[dict],
    tags: list[str] | None = None,
) -> dict:
    """Monta metadado v2 fechado, ordenado e sem duplicata exata."""

    unique: dict[tuple[str, str, str], dict] = {}
    for record in records:
        publication_format = validate_format(record.get("format"))
        url = validate_source_url(record.get("url"), https_only=False)
        hashes = record.get("hashes")
        if not isinstance(hashes, dict) or set(hashes) != {"sha1", "sha256", "sha512"}:
            raise ContractError("registro sem hashes fechados")
        for name, length in (("sha1", 40), ("sha256", 64), ("sha512", 128)):
            if not re.fullmatch(rf"[0-9a-f]{{{length}}}", str(hashes[name])):
                raise ContractError(f"{name} invalido em registro")
        accessed_at = record.get("accessed_at")
        if isinstance(accessed_at, (int, float)):
            accessed_at = datetime.fromtimestamp(accessed_at, timezone.utc).isoformat()
        if not isinstance(accessed_at, str) or not accessed_at:
            raise ContractError("accessed_at ausente")
        size = record.get("size")
        if not isinstance(size, int) or size <= 0:
            raise ContractError("size invalido")
        normalized = {
            "format": publication_format,
            "url": url,
            "accessed_at": accessed_at,
            "size": size,
            "hashes": {name: hashes[name] for name in ("sha1", "sha256", "sha512")},
        }
        key = (publication_format, url, hashes["sha256"])
        unique[key] = normalized
    normalized_tags = sorted(set(tags or []))
    for tag in normalized_tags:
        validate_slug(tag, "tag")
    return {
        "schema_version": SOURCE_SCHEMA,
        "identity": {
            "author": identity.author,
            "language": identity.language,
            "type": identity.publication_type,
            "title": identity.title,
            "acronym": identity.acronym,
            "tags": normalized_tags,
        },
        "sources": sorted(unique.values(), key=source_record_sort_key),
    }


def write_json_atomic(path: Path | str, data: dict) -> None:
    """Grava JSON deterministico por replace atomico no mesmo diretorio."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=target.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        for attempt in range(8):
            try:
                os.replace(temporary, target)
                break
            except PermissionError:
                if attempt == 7:
                    raise
                time.sleep(min(0.01 * (2**attempt), 0.25))
    finally:
        temporary.unlink(missing_ok=True)
