# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Validação, progresso retomável e commit atômico de uma publicação."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Callable, Iterable, TypeVar
import zipfile

from acquisition import AcquisitionLedger, CatalogItem
from publication_contract import (
    ContractError,
    REPOSITORY_ROOT,
    hash_file,
    validate_file_signature,
)
from structured_content import validate_structured_artifact


MANIFEST_SCHEMA = "publication-chunking-analysis/v2"
PROGRESS_SCHEMA = "publication-global-progress/v2"
LEGACY_PROGRESS_SCHEMA = "publication-global-progress/v1"
T = TypeVar("T")


ALLOWED_CANONICAL_SUFFIXES = {
    ".epub",
    ".jpeg",
    ".jpg",
    ".json",
    ".md",
    ".pdf",
    ".png",
    ".svg",
    ".webp",
}
FORBIDDEN_NAMES = {"__pycache__", "cache", "logs", "sessions", "tmp"}
FORBIDDEN_SUFFIXES = {
    ".lock",
    ".log",
    ".partial",
    ".pid",
    ".sqlite",
    ".tmp",
    ".wal",
}


class PublicationTransactionError(ContractError):
    """Bloqueia uma transação sem tocar alterações alheias."""


def _write_json_atomic(path: Path, value: dict) -> None:
    """Persiste estado de runtime sem expor janela de arquivo parcial."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def progress_fingerprint(value: object) -> str:
    """Identifica somente configuração/algoritmo causal do diário global."""

    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class GlobalProgressJournal:
    """Registra o limite global confirmado e aceita apenas crescimento apenso."""

    def __init__(
        self,
        path: Path,
        *,
        tool: str,
        scope: str,
        fingerprint: str,
        order: list[str],
        legacy_fingerprints: Iterable[str] = (),
        reset: bool = False,
    ) -> None:
        self.path = path.resolve()
        self.tool = tool
        self.scope = scope
        self.fingerprint = fingerprint
        self.legacy_fingerprints = frozenset(legacy_fingerprints)
        if any(
            re.fullmatch(r"[0-9a-f]{64}", value) is None
            for value in self.legacy_fingerprints
        ):
            raise PublicationTransactionError("fingerprint legado inválido")
        self.order = list(order)
        if len(self.order) != len(set(self.order)):
            raise PublicationTransactionError("diário global possui ordem duplicada")
        if reset:
            self.path.unlink(missing_ok=True)
        self.document = self._load()

    @property
    def next_index(self) -> int:
        return int(self.document["next_index"])

    def is_confirmed(self, identity: str) -> bool:
        """Informa se a unidade já possui confirmação durável, sem exigir contiguidade."""

        return identity in set(self.document["confirmed"])

    def _initial(self) -> dict:
        return {
            "schema_version": PROGRESS_SCHEMA,
            "tool": self.tool,
            "scope": self.scope,
            "fingerprint": self.fingerprint,
            "order": self.order,
            "confirmed": [],
            "next_index": 0,
            "current": None,
            "last_confirmed": None,
            "status": "running",
        }

    def _load(self) -> dict:
        if not self.path.exists():
            document = self._initial()
            _write_json_atomic(self.path, document)
            return document
        try:
            document = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PublicationTransactionError(
                f"diário global corrompido; use reset explícito: {self.path}"
            ) from error
        legacy_required = {
            "schema_version",
            "tool",
            "scope",
            "fingerprint",
            "order",
            "next_index",
            "current",
            "last_confirmed",
            "status",
        }
        required = {*legacy_required, "confirmed"}
        if not isinstance(document, dict):
            raise PublicationTransactionError(
                f"diário global incompatível; use reset explícito: {self.path}"
            )
        schema_migration = False
        if (
            set(document) == legacy_required
            and document.get("schema_version") == LEGACY_PROGRESS_SCHEMA
            and isinstance(document.get("order"), list)
            and isinstance(document.get("next_index"), int)
            and document.get("fingerprint") in self.legacy_fingerprints
        ):
            legacy_order = document["order"]
            legacy_next = document["next_index"]
            if 0 <= legacy_next <= len(legacy_order):
                document["schema_version"] = PROGRESS_SCHEMA
                document["confirmed"] = legacy_order[:legacy_next]
                schema_migration = True

        fingerprint_migration = (
            document.get("fingerprint") in self.legacy_fingerprints
        )

        stored_order = document.get("order")
        next_index = document.get("next_index")
        confirmed = document.get("confirmed")
        order_compatible = (
            isinstance(stored_order, list)
            and len(stored_order) == len(set(stored_order))
            and all(value in self.order for value in stored_order)
            and [value for value in self.order if value in set(stored_order)] == stored_order
        )
        if (
            set(document) != required
            or document.get("schema_version") != PROGRESS_SCHEMA
            or document.get("tool") != self.tool
            or document.get("scope") != self.scope
            or (
                document.get("fingerprint") != self.fingerprint
                and not fingerprint_migration
            )
            or not isinstance(stored_order, list)
            or not all(isinstance(value, str) and value for value in stored_order)
            or not isinstance(next_index, int)
            or next_index < 0
            or next_index > len(stored_order)
            or not order_compatible
            or not isinstance(confirmed, list)
            or len(confirmed) != len(set(confirmed))
            or not all(value in stored_order for value in confirmed)
        ):
            raise PublicationTransactionError(
                f"diário global incompatível; use reset explícito: {self.path}"
            )
        appended = [value for value in self.order if value not in set(stored_order)]
        self.order = [*stored_order, *appended]
        if fingerprint_migration:
            document["fingerprint"] = self.fingerprint
        if appended:
            document["order"] = self.order
            document["status"] = "running"
        confirmed_set = set(document["confirmed"])
        document["confirmed"] = [value for value in self.order if value in confirmed_set]
        document["next_index"] = next(
            (
                position
                for position, value in enumerate(self.order)
                if value not in confirmed_set
            ),
            len(self.order),
        )
        document["status"] = (
            "completed" if len(confirmed_set) == len(self.order) else "running"
        )
        _write_json_atomic(self.path, document)
        return document

    def record(self, position: int, identity: str, phase: str) -> None:
        """Atualiza a fase corrente sem avançar o limite confirmado."""

        if position < 0 or position >= len(self.order):
            raise PublicationTransactionError("posição inválida no diário global")
        if self.order[position] != identity:
            raise PublicationTransactionError("identidade divergente no diário global")
        if self.is_confirmed(identity):
            raise PublicationTransactionError("unidade já confirmada no diário global")
        self.document["current"] = {
            "position": position,
            "identity": identity,
            "phase": phase,
        }
        self.document["status"] = "running"
        _write_json_atomic(self.path, self.document)

    def confirm(self, position: int, identity: str, *, commit: str | None = None) -> None:
        """Confirma uma unidade concluída sem bloquear coleções independentes."""

        if position < 0 or position >= len(self.order) or self.order[position] != identity:
            raise PublicationTransactionError("confirmação divergente no diário global")
        if self.is_confirmed(identity):
            raise PublicationTransactionError("unidade já confirmada no diário global")
        confirmed = set(self.document["confirmed"])
        confirmed.add(identity)
        self.document["confirmed"] = [
            value for value in self.order if value in confirmed
        ]
        self.document["next_index"] = next(
            (
                candidate
                for candidate, value in enumerate(self.order)
                if value not in confirmed
            ),
            len(self.order),
        )
        self.document["current"] = None
        self.document["last_confirmed"] = {
            "position": position,
            "identity": identity,
            "commit": commit,
        }
        self.document["status"] = (
            "completed" if len(confirmed) == len(self.order) else "running"
        )
        _write_json_atomic(self.path, self.document)


def _inside(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    resolved_root = root.resolve()
    return resolved == resolved_root or resolved_root in resolved.parents


def _read_metadata(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise PublicationTransactionError(f"metadado inválido: {path}") from error
    if value.get("schema_version") != "publication-source/v3":
        raise PublicationTransactionError("transação exige publication-source/v3")
    if value.get("state") != "completed":
        raise PublicationTransactionError("publicação ainda não está completed")
    return value


def catalog_item_from_publication(directory: Path) -> CatalogItem:
    """Reconstrói a identidade transacional exclusivamente do metadado v3."""

    candidates = sorted(directory.glob("*.source.json"))
    if len(candidates) != 1:
        raise PublicationTransactionError("publicação sem metadado v3 inequívoco")
    document = _read_metadata(candidates[0])
    identity = document.get("identity") or {}
    collection = document.get("collection") or {}
    required = (
        "remote_id",
        "author_original",
        "author_key",
        "title_original",
        "title_normalized",
        "language_original",
        "language",
        "language_path",
        "category_original",
        "category",
        "type",
        "public_url",
    )
    if any(not isinstance(identity.get(key), str) or not identity[key] for key in required):
        raise PublicationTransactionError("identidade v3 incompleta")
    if not isinstance(collection.get("id"), str) or not collection["id"]:
        raise PublicationTransactionError("coleção v3 incompleta")
    return CatalogItem(
        remote_id=identity["remote_id"],
        collection_id=collection["id"],
        collection_name=str(collection.get("name") or collection["id"]),
        author_name=identity["author_original"],
        author_key=identity["author_key"],
        language_original=identity["language_original"],
        language=identity["language"],
        language_path=identity["language_path"],
        publication_type=identity["type"],
        title_original=identity["title_original"],
        title_normalized=identity["title_normalized"],
        public_url=identity["public_url"],
        category_name=identity["category_original"],
        category_path=identity["category"],
        edition=str(identity.get("edition") or ""),
        local_complete=True,
    )


def _matching_asset(directory: Path, record: dict) -> Path:
    publication_format = record.get("format")
    hashes = record.get("hashes") or {}
    expected = hashes.get("sha256")
    if publication_format not in {"pdf", "epub"} or not re.fullmatch(
        r"[0-9a-f]{64}", str(expected or "")
    ):
        raise PublicationTransactionError("fonte nativa sem formato/hash válido")
    matches = []
    for candidate in sorted(directory.glob(f"*.{publication_format}")):
        if candidate.is_symlink() or not candidate.is_file():
            continue
        validate_file_signature(candidate, publication_format)
        evidence = hash_file(candidate)
        if evidence.sha256 == expected and evidence.size == record.get("size"):
            matches.append(candidate)
    if len(matches) != 1:
        raise PublicationTransactionError(
            f"fonte {publication_format} não possui pareamento inequívoco"
        )
    return matches[0]


def validate_complete_publication(
    item: CatalogItem,
    source_root: Path,
    repository_root: Path = REPOSITORY_ROOT,
    *,
    require_intelligence: bool = True,
) -> list[Path]:
    """Retorna allowlist canônica somente para unidade completa e pareada."""

    identity = item.publication_identity()
    directory = source_root / identity.relative_directory()
    if not _inside(directory, source_root) or not directory.is_dir():
        raise PublicationTransactionError("diretório canônico ausente ou inseguro")
    metadata_path = directory / identity.metadata_name()
    document = _read_metadata(metadata_path)
    metadata_identity = document.get("identity") or {}
    expected_identity = {
        "remote_id": item.remote_id,
        "author_key": item.author_key,
        "language": item.language,
        "category": item.category_path,
        "type": item.publication_type,
        "acronym": identity.acronym,
        "route_slug": identity.route_slug,
    }
    for key, expected in expected_identity.items():
        if metadata_identity.get(key) != expected:
            raise PublicationTransactionError(f"identidade divergente: {key}")

    sources = document.get("sources")
    segments = document.get("segments")
    derivations = document.get("derivations")
    if not isinstance(sources, list) or not sources:
        raise PublicationTransactionError("publicação sem fontes")
    if not isinstance(segments, list) or not isinstance(derivations, list):
        raise PublicationTransactionError("estrutura v3 incompleta")

    referenced: set[Path] = {metadata_path}
    native_sources = [record for record in sources if record.get("format") in {"pdf", "epub"}]
    for record in native_sources:
        referenced.add(_matching_asset(directory, record))

    for record in segments:
        relative = record.get("path")
        expected_hash = record.get("sha256")
        if not isinstance(relative, str) or not re.fullmatch(
            r"[0-9a-f]{64}", str(expected_hash or "")
        ):
            raise PublicationTransactionError("segmento sem path/hash")
        if "!/" in relative:
            archive_relative, internal = relative.split("!/", 1)
            candidate = (directory / archive_relative).resolve()
            if (
                not _inside(candidate, directory)
                or candidate.suffix.casefold() != ".epub"
                or not candidate.is_file()
                or not internal.startswith("META-INF/egwsearch-source/")
                or Path(internal).name != internal.rsplit("/", 1)[-1]
            ):
                raise PublicationTransactionError("segmento interno ausente ou fora da unidade")
            try:
                with zipfile.ZipFile(candidate) as archive:
                    value = archive.read(internal)
            except (OSError, KeyError, zipfile.BadZipFile) as error:
                raise PublicationTransactionError("segmento interno EPUB ausente") from error
            if hashlib.sha256(value).hexdigest() != expected_hash:
                raise PublicationTransactionError("hash de segmento interno divergente")
            referenced.add(candidate)
        else:
            candidate = (directory / relative).resolve()
            if not _inside(candidate, directory) or not candidate.is_file():
                raise PublicationTransactionError("segmento ausente ou fora da unidade")
            if hash_file(candidate).sha256 != expected_hash:
                raise PublicationTransactionError("hash de segmento divergente")
            referenced.add(candidate)

    structured_assets: list[Path] = []
    for record in derivations:
        relative = record.get("path")
        hashes = record.get("hashes") or {}
        if not isinstance(relative, str) or not re.fullmatch(
            r"[0-9a-f]{64}", str(hashes.get("sha256") or "")
        ):
            raise PublicationTransactionError("derivado sem path/hash")
        candidate = (directory / relative).resolve()
        if not _inside(candidate, directory) or not candidate.is_file():
            raise PublicationTransactionError("derivado ausente ou fora da unidade")
        evidence = hash_file(candidate)
        if evidence.sha256 != hashes["sha256"] or evidence.size != record.get("size"):
            raise PublicationTransactionError("derivado divergente")
        if record.get("format") == "epub":
            validate_file_signature(candidate, "epub")
        if record.get("method") == "structured-json":
            if record.get("encoding") != "utf-8" or record.get("format") != "json":
                raise PublicationTransactionError("derivado estruturado sem UTF-8/JSON")
            try:
                validate_structured_artifact(
                    candidate,
                    str(record.get("model") or "") or None,
                )
            except ContractError as error:
                raise PublicationTransactionError("derivado estruturado inválido") from error
            structured_assets.append(candidate)
        referenced.add(candidate)

    editorial_assets = sorted(
        path
        for path in referenced
        if path.suffix.casefold() in {".epub", ".pdf"}
    )
    analyzable_assets = sorted(set(editorial_assets + structured_assets))
    if not analyzable_assets:
        raise PublicationTransactionError("publicação sem EPUB/PDF/JSON estruturado analisável")
    for asset in analyzable_assets if require_intelligence else []:
        manifest_path = asset.with_name(f"{asset.name}.chunking.json")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PublicationTransactionError(
                f"manifesto de chunking ausente ou inválido: {asset.name}"
            ) from error
        evidence = hash_file(asset)
        declared = (manifest.get("asset") or {}) if isinstance(manifest, dict) else {}
        if (
            manifest.get("schema_version") != MANIFEST_SCHEMA
            or declared.get("size") != evidence.size
            or (declared.get("hashes") or {}).get("sha512") != evidence.sha512
            or declared.get("format") != asset.suffix.casefold().lstrip(".")
            or not isinstance(manifest.get("experiments"), list)
            or not isinstance(manifest.get("reference"), dict)
            or not isinstance(manifest.get("recommendation"), dict)
            or not isinstance(manifest.get("catalog"), dict)
        ):
            raise PublicationTransactionError(
                f"manifesto de chunking divergente: {asset.name}"
            )
        if asset.suffix.casefold() == ".json":
            reference = manifest.get("reference") or {}
            if (
                reference.get("semantic_model") not in {"scripture", "lexical", "concordance"}
                or not isinstance(reference.get("natural_units"), int)
                or reference["natural_units"] <= 0
                or not isinstance(reference.get("first_identity"), dict)
                or not isinstance(reference.get("last_identity"), dict)
            ):
                raise PublicationTransactionError(
                    f"manifesto semântico divergente: {asset.name}"
                )
        referenced.add(manifest_path)

    files = sorted(path for path in directory.rglob("*") if path.is_file())
    if not files:
        raise PublicationTransactionError("unidade canônica vazia")
    for path in files:
        relative_parts = {part.casefold() for part in path.relative_to(directory).parts}
        if path.is_symlink() or relative_parts & FORBIDDEN_NAMES:
            raise PublicationTransactionError(f"estado de runtime na unidade: {path.name}")
        suffix = path.suffix.casefold()
        if suffix in FORBIDDEN_SUFFIXES or suffix not in ALLOWED_CANONICAL_SUFFIXES:
            raise PublicationTransactionError(f"arquivo não canônico na unidade: {path.name}")
        if path.stat().st_size <= 0:
            raise PublicationTransactionError(f"arquivo vazio na unidade: {path.name}")
    if not referenced.issubset(set(files)):
        raise PublicationTransactionError("referência canônica ausente")
    return [path.relative_to(repository_root) for path in files]


def _git(root: Path, arguments: Iterable[str], *, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", "-c", "maintenance.auto=false", *arguments],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).decode("utf-8", "replace").strip()
        raise PublicationTransactionError(f"git {' '.join(arguments)} falhou: {detail}")
    return result


def _nul_paths(payload: bytes) -> list[str]:
    return [part.decode("utf-8", "surrogateescape") for part in payload.split(b"\0") if part]


def _status_paths(root: Path, relative_directory: Path) -> set[str]:
    result = _git(
        root,
        ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--", relative_directory.as_posix()],
    )
    parts = _nul_paths(result.stdout)
    paths: set[str] = set()
    index = 0
    while index < len(parts):
        entry = parts[index]
        if len(entry) < 4:
            raise PublicationTransactionError("status Git inválido")
        code = entry[:2]
        paths.add(entry[3:].replace("\\", "/"))
        index += 2 if "R" in code or "C" in code else 1
    return paths


def _metadata_remote_id_bytes(payload: bytes) -> str:
    try:
        document = json.loads(payload.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return ""
    if not isinstance(document, dict):
        return ""
    return str((document.get("identity") or {}).get("remote_id") or "")


def _metadata_remote_id(path: Path) -> str:
    try:
        return _metadata_remote_id_bytes(path.read_bytes())
    except OSError:
        return ""


def _head_metadata_remote_id(root: Path, metadata_path: Path) -> str:
    relative = metadata_path.resolve().relative_to(root.resolve()).as_posix()
    result = _git(root, ["show", f"HEAD:{relative}"], check=False)
    return _metadata_remote_id_bytes(result.stdout) if result.returncode == 0 else ""


def _snapshot_changed_paths(
    root: Path,
    recovery_root: Path,
    changed: set[str],
    *,
    reason: str,
) -> Path | None:
    """Copia bytes divergentes para runtime antes de qualquer reconciliação."""

    if not changed:
        return None
    evidence: list[dict] = []
    for relative in sorted(changed):
        candidate = (root / relative).resolve()
        if not _inside(candidate, root):
            raise PublicationTransactionError("path divergente fora do repositório")
        record: dict = {"path": relative, "exists": candidate.is_file()}
        if candidate.is_file():
            record["sha256"] = hashlib.sha256(candidate.read_bytes()).hexdigest()
            record["size"] = candidate.stat().st_size
        evidence.append(record)
    fingerprint = hashlib.sha256(
        json.dumps(evidence, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:24]
    destination = recovery_root / "snapshots" / fingerprint
    manifest = destination / "recovery.json"
    if manifest.is_file():
        return destination
    for record in evidence:
        if not record["exists"]:
            continue
        source = root / str(record["path"])
        target = destination / "files" / str(record["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    _write_json_atomic(
        manifest,
        {
            "schema_version": "publication-recovery/v1",
            "kind": "non-destructive-snapshot",
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files": evidence,
        },
    )
    return destination


def recover_tracked_publication(
    repository_root: Path,
    source_root: Path,
    directory: Path,
    recovery_root: Path,
    *,
    reason: str,
    expected_remote_id: str,
) -> Path:
    """Restaura uma unidade rastreada com rollback e cópia integral auditável."""

    root = repository_root.resolve()
    source = source_root.resolve()
    target = directory.resolve()
    if not _inside(target, source) or target == source or not _inside(target, root):
        raise PublicationTransactionError("unidade de recuperação fora da fonte")
    relative = target.relative_to(root)
    tracked = _nul_paths(
        _git(root, ["ls-tree", "-r", "--name-only", "-z", "HEAD", "--", relative.as_posix()]).stdout
    )
    if not tracked:
        raise PublicationTransactionError("unidade divergente não possui base Git confiável")
    fingerprint = hashlib.sha256(
        f"{relative.as_posix()}\0{reason}\0{expected_remote_id}".encode("utf-8")
    ).hexdigest()[:24]
    destination = recovery_root / "transactions" / fingerprint
    backup = destination / "tree"
    if destination.exists():
        destination = destination.with_name(
            f"{destination.name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
        )
        backup = destination / "tree"
    destination.mkdir(parents=True, exist_ok=False)
    if target.is_dir():
        shutil.copytree(target, backup)
    _write_json_atomic(
        destination / "recovery.json",
        {
            "schema_version": "publication-recovery/v1",
            "kind": "tracked-publication-rollback",
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "path": relative.as_posix(),
            "expected_remote_id": expected_remote_id,
            "tracked_files": sorted(tracked),
        },
    )
    try:
        if target.is_dir():
            shutil.rmtree(target)
        for tracked_relative in tracked:
            restored = (root / tracked_relative).resolve()
            if not _inside(restored, target):
                raise PublicationTransactionError("snapshot Git contém path fora da unidade")
            payload = _git(root, ["show", f"HEAD:{tracked_relative}"]).stdout
            restored.parent.mkdir(parents=True, exist_ok=True)
            restored.write_bytes(payload)
        metadata = sorted(target.glob("*.source.json"))
        if len(metadata) != 1 or _metadata_remote_id(metadata[0]) != expected_remote_id:
            raise PublicationTransactionError("snapshot Git não restaurou a identidade esperada")
        remaining = _status_paths(root, relative)
        if remaining:
            raise PublicationTransactionError(
                "unidade restaurada ainda diverge do snapshot Git: "
                + ", ".join(sorted(remaining))
            )
        return destination
    except Exception:
        if target.is_dir():
            shutil.rmtree(target)
        if backup.is_dir():
            shutil.copytree(backup, target)
        raise


@contextmanager
def _exclusive_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    token = f"{os.getpid()}\n"
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise PublicationTransactionError("outra finalização Git está ativa ou exige inspeção") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(token)
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        try:
            if path.read_text(encoding="utf-8") == token:
                path.unlink()
        except OSError:
            pass


@contextmanager
def exclusive_process_lock(path: Path):
    """Serializa uma execução longa com lock de SO que não deixa stale lock."""

    path.parent.mkdir(parents=True, exist_ok=True)
    stream = path.open("a+b")
    locked = False
    try:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except OSError as error:
            raise PublicationTransactionError(
                "outra execução canônica do downloader está ativa"
            ) from error
        stream.seek(0)
        stream.truncate()
        stream.write(f"{os.getpid()}\n".encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
        yield
    finally:
        if locked:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


class GitPublicationPublisher:
    """Serializa staging/commit sem absorver a worktree do desenvolvedor."""

    def __init__(
        self,
        repository_root: Path,
        source_root: Path,
        lock_path: Path,
        branch: str = "dev",
        index_path: Path | None = None,
        global_paths: Iterable[Path] | None = None,
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.source_root = source_root.resolve()
        self.lock_path = lock_path.resolve()
        self.branch = branch
        self.index_path = (
            index_path.resolve()
            if index_path is not None
            else (self.source_root / "index.json").resolve()
        )
        if not _inside(self.index_path, self.source_root):
            raise PublicationTransactionError("índice global fora da fonte")
        defaults = {
            self.index_path,
            self.index_path.with_name(
                f"{self.index_path.stem}.manifest{self.index_path.suffix}"
            ),
            self.source_root / "chunking-learning.json",
        }
        self.global_paths = {
            Path(path).resolve() for path in (global_paths or defaults)
        }
        if self.index_path not in self.global_paths:
            self.global_paths.add(self.index_path)
        if any(not _inside(path, self.source_root) for path in self.global_paths):
            raise PublicationTransactionError("artefato global fora da fonte")

    def _validate_global_index(self, item: CatalogItem) -> None:
        """Confirma a saída da capacidade canônica sem reserializá-la."""

        try:
            document = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PublicationTransactionError("índice global ausente ou inválido") from error
        if (
            not isinstance(document, dict)
            or document.get("schema_version") != "publication-global-index/v1"
            or not isinstance(document.get("publications"), list)
        ):
            raise PublicationTransactionError("contrato do índice global divergente")
        metadata_path = (
            item.publication_identity().relative_directory()
            / item.publication_identity().metadata_name()
        ).as_posix()
        matches = [
            entry
            for entry in document["publications"]
            if isinstance(entry, dict)
            and (entry.get("metadata") or {}).get("path") == metadata_path
        ]
        if len(matches) != 1:
            raise PublicationTransactionError("publicação ausente ou duplicada no índice global")

    def _validate_repository(self) -> None:
        inside = _git(self.repository_root, ["rev-parse", "--is-inside-work-tree"]).stdout.strip()
        if inside != b"true":
            raise PublicationTransactionError("diretório não é repositório Git")
        branch = _git(self.repository_root, ["branch", "--show-current"]).stdout.decode().strip()
        if branch != self.branch:
            raise PublicationTransactionError(f"commit exige branch {self.branch}")
    def preflight(self, item: CatalogItem, *, resume: bool = False) -> None:
        """Preserva estado parcial da unidade e deixa a etapa idempotente repará-lo."""

        self._validate_repository()
        directory = self.source_root / item.publication_identity().relative_directory()
        relative = directory.relative_to(self.repository_root)
        unit_dirty = _status_paths(self.repository_root, relative)
        if unit_dirty and not resume:
            _snapshot_changed_paths(
                self.repository_root,
                self.lock_path.parent.parent / "recovery",
                unit_dirty,
                reason=f"preflight:{item.collection_id}:{item.remote_id}",
            )

    def resolve_item_identity(self, item: CatalogItem) -> CatalogItem:
        """Reserva uma rota física sem permitir que IDs remotos se sobrescrevam."""

        base_item = replace(item, route_slug="", acronym="")
        base_identity = base_item.publication_identity()
        base_directory = self.source_root / base_identity.relative_directory()
        base_metadata = base_directory / base_identity.metadata_name()
        current_remote_id = _metadata_remote_id(base_metadata)
        committed_remote_id = _head_metadata_remote_id(
            self.repository_root, base_metadata
        )
        if (
            committed_remote_id == item.remote_id
            and current_remote_id
            and current_remote_id != item.remote_id
        ):
            recover_tracked_publication(
                self.repository_root,
                self.source_root,
                base_directory,
                self.lock_path.parent.parent / "recovery",
                reason=(
                    f"identity-regression:{committed_remote_id}->{current_remote_id}"
                ),
                expected_remote_id=committed_remote_id,
            )
            return base_item
        occupant = committed_remote_id or current_remote_id
        if not occupant or occupant == item.remote_id:
            return base_item

        if current_remote_id == item.remote_id and committed_remote_id:
            recover_tracked_publication(
                self.repository_root,
                self.source_root,
                base_directory,
                self.lock_path.parent.parent / "recovery",
                reason=(
                    f"identity-collision:{committed_remote_id}->{item.remote_id}"
                ),
                expected_remote_id=committed_remote_id,
            )

        discriminator = re.sub(r"[^a-z0-9]+", "-", item.remote_id.casefold()).strip("-")
        if not discriminator:
            discriminator = item.stable_key()[:12]
        route_slug = f"{base_identity.route_slug}-{discriminator}"
        resolved = replace(
            item,
            route_slug=route_slug,
            acronym=base_identity.acronym,
        )
        resolved_identity = resolved.publication_identity()
        resolved_metadata = (
            self.source_root
            / resolved_identity.relative_directory()
            / resolved_identity.metadata_name()
        )
        resolved_occupant = _metadata_remote_id(resolved_metadata) or _head_metadata_remote_id(
            self.repository_root, resolved_metadata
        )
        if resolved_occupant and resolved_occupant != item.remote_id:
            resolved = replace(
                resolved,
                route_slug=f"{route_slug}-{item.stable_key()[:8]}",
            )
        return resolved

    def finalize(
        self,
        item: CatalogItem,
        ledger: AcquisitionLedger,
        operation: Callable[[], T],
    ) -> tuple[T, str | None]:
        """Serializa inteligência, validação, staging e commit como uma unidade."""

        with _exclusive_lock(self.lock_path):
            self._validate_repository()
            result = operation()
            paths = validate_complete_publication(
                item,
                self.source_root,
                self.repository_root,
            )
            return result, self._commit_locked(item, paths, ledger)

    def commit(
        self,
        item: CatalogItem,
        paths: list[Path],
        ledger: AcquisitionLedger,
    ) -> str | None:
        with _exclusive_lock(self.lock_path):
            return self._commit_locked(item, paths, ledger)

    def _commit_locked(
        self,
        item: CatalogItem,
        paths: list[Path],
        ledger: AcquisitionLedger,
    ) -> str | None:
        """Executa o efeito Git sob lock já adquirido pelo fechamento."""

        self._validate_repository()
        allowed = {path.as_posix() for path in paths}
        global_relatives = {
            path.relative_to(self.repository_root).as_posix()
            for path in self.global_paths
        }
        allowed.update(global_relatives)
        runtime_relative = self.lock_path.parent.parent.relative_to(self.repository_root).as_posix()
        if any(path == runtime_relative or path.startswith(f"{runtime_relative}/") for path in allowed):
            raise PublicationTransactionError("allowlist contém estado de runtime")
        directory = self.source_root / item.publication_identity().relative_directory()
        relative_directory = directory.relative_to(self.repository_root)
        key = item.stable_key()
        created_commit: str | None = None
        changed: set[str] = set()
        try:
            self._validate_repository()
            self._validate_global_index(item)
            changed = _status_paths(self.repository_root, relative_directory)
            for global_path in sorted(self.global_paths):
                changed.update(
                    _status_paths(
                        self.repository_root,
                        global_path.relative_to(self.repository_root),
                    )
                )
            if not changed:
                return None
            if not changed.issubset(allowed):
                raise PublicationTransactionError(
                    f"alteração fora da allowlist: {', '.join(sorted(changed - allowed))}"
                )
            _git(self.repository_root, ["add", "--", *sorted(changed)])
            staged = set(
                _nul_paths(
                    _git(
                        self.repository_root,
                        ["diff", "--cached", "--name-only", "-z", "--", *sorted(changed)],
                    ).stdout
                )
            )
            if staged != changed:
                raise PublicationTransactionError("staging diverge da unidade calculada")
            worktree_changed = _nul_paths(
                _git(
                    self.repository_root,
                    ["diff", "--name-only", "-z", "--", *sorted(changed)],
                ).stdout
            )
            if worktree_changed:
                raise PublicationTransactionError(
                    "unidade mudou após staging; commit interrompido"
                )
            title = " ".join(item.title_normalized.split())[:96]
            message = f"publicação: adiciona {item.remote_id} {title}"
            before = _git(self.repository_root, ["rev-parse", "HEAD"]).stdout.decode().strip()
            result = _git(
                self.repository_root,
                ["commit", "-m", message, "--", *sorted(changed)],
                check=False,
            )
            after = _git(self.repository_root, ["rev-parse", "HEAD"]).stdout.decode().strip()
            if result.returncode != 0 and after == before:
                detail = (result.stderr or result.stdout).decode("utf-8", "replace").strip()
                raise PublicationTransactionError(f"commit falhou: {detail}")
            if after == before:
                raise PublicationTransactionError("commit não alterou HEAD")
            created_commit = after
            committed = set(
                _nul_paths(
                    _git(
                        self.repository_root,
                        ["diff-tree", "--no-commit-id", "--name-only", "-r", "-z", after],
                    ).stdout
                )
            )
            if committed != changed:
                ledger.transition(
                    key,
                    "completed",
                    git_state="commit_review",
                    commit=after,
                )
                raise PublicationTransactionError(
                    "commit criado com conteúdo diferente da unidade calculada"
                )
            ledger.transition(key, "completed", git_state="committed", commit=after)
            return after
        except Exception:
            if created_commit is None:
                if changed:
                    _git(
                        self.repository_root,
                        ["restore", "--staged", "--", *sorted(changed)],
                        check=False,
                    )
                ledger.transition(key, "completed", git_state="commit_pending")
            raise
