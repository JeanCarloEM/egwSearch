# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Contratos incrementais e derivados do adaptador público EGW Writings.

O módulo usa somente a biblioteca padrão. Rede, navegador e barra de progresso
continuam opcionais e pertencem à CLI em ``baixar.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import random
import re
import threading
import time
from typing import Callable, Iterable
from urllib.parse import urlsplit
import zipfile

from publication_contract import (
    ContractError,
    PublicationIdentity,
    publication_identity,
    uri_slug,
    write_json_atomic,
)


STATE_SCHEMA = "publication-acquisition-state/v1"
SOURCE_SCHEMA_V3 = "publication-source/v3"
ALLOWED_STATES = {
    "pending",
    "processing",
    "completed",
    "skipped",
    "incomplete",
    "corrupt",
    "unavailable",
    "ineligible",
    "temporary_failure",
    "permanent_failure",
    "review_required",
}
BLOCK_MARKERS = (
    "cf-chl-",
    "captcha",
    "challenge-platform",
    "checking your browser",
    "cloudflare",
    "cf-turnstile",
    "g-recaptcha",
    "hcaptcha",
    "human verification",
    "verificacao humana",
    "verificação humana",
    "are you human",
    "verify you are human",
    "confirme que voce e humano",
    "confirme que você é humano",
    "unusual traffic",
    "too many requests",
    "enable javascript and cookies to continue",
)
TYPE_ALIASES = {
    "book": "books",
    "books": "books",
    "livro": "livros",
    "livros": "livros",
    "devotional": "devotionals",
    "devotionals": "devotionals",
    "devocional": "devocionais",
    "devocionais": "devocionais",
    "pamphlet": "pamphlets",
    "pamphlets": "pamphlets",
    "periodical": "periodicals",
    "periodicals": "periodicals",
    "misc": "misc",
    "manuscript": "manuscript",
    "article": "articles",
    "articles": "articles",
}


class OriginBlocked(RuntimeError):
    """Sinaliza contenção que exige parada sem nova tentativa."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_language(value: str) -> tuple[str, str]:
    """Retorna ``(idioma editorial, segmento de path)`` para o escopo aceito."""

    if not isinstance(value, str) or not value.strip():
        raise ContractError("idioma ausente")
    normalized = re.sub(r"[_\s]+", "-", value.strip()).casefold()
    if normalized in {
        "pt",
        "pt-br",
        "portuguese",
        "portuguese-brazil",
        "português",
        "português-brasileiro",
    }:
        return "pt-BR", "pt-br"
    if normalized in {
        "en",
        "en-us",
        "en-gb",
        "english",
        "inglês",
    }:
        return "en", "en"
    raise ContractError(f"idioma nao elegivel: {value!r}")


def canonical_author_key(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ContractError("autor ausente")
    return uri_slug(name)


def canonical_publication_type(value: str, language: str) -> str:
    if not isinstance(value, str) or not value.strip():
        return "livros" if canonical_language(language)[0] == "pt-BR" else "books"
    normalized = uri_slug(value).replace("-", " ")
    publication_type = TYPE_ALIASES.get(normalized, uri_slug(value))
    if publication_type == "books" and canonical_language(language)[0] == "pt-BR":
        return "livros"
    if publication_type == "devotionals" and canonical_language(language)[0] == "pt-BR":
        return "devocionais"
    return publication_type


def remote_id_from_url(url: str) -> str:
    path = urlsplit(url).path
    match = re.search(r"/(?:book|read)/(?:b)?(\d+)(?:[./]|$)", path, re.I)
    if not match:
        raise ContractError(f"URL sem identificador remoto: {url}")
    return match.group(1)


@dataclass(frozen=True)
class CatalogAsset:
    format: str
    url: str
    etag: str = ""
    last_modified: str = ""
    size: int | None = None
    remote_hash: str = ""


@dataclass(frozen=True)
class CatalogSegment:
    remote_id: str
    url: str
    order: int
    title: str
    html: str


@dataclass(frozen=True)
class CatalogItem:
    remote_id: str
    collection_id: str
    collection_name: str
    author_name: str
    author_key: str
    language_original: str
    language: str
    language_path: str
    publication_type: str
    title_original: str
    title_normalized: str
    public_url: str
    edition: str = ""
    assets: tuple[CatalogAsset, ...] = ()
    segments: tuple[CatalogSegment, ...] = ()

    def publication_identity(self) -> PublicationIdentity:
        return publication_identity(
            self.author_key,
            self.language_path,
            self.publication_type,
            self.title_normalized,
        )

    def stable_key(self) -> str:
        material = "\0".join(
            (
                self.collection_id,
                self.remote_id,
                self.author_key,
                self.language,
                self.publication_type,
                self.title_normalized,
                self.edition,
            )
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _payload_items(payload: object) -> list[dict]:
    if isinstance(payload, list):
        values = payload
    elif isinstance(payload, dict):
        values = None
        for key in ("publications", "books", "items", "results", "data"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                values = candidate
                break
            if isinstance(candidate, dict):
                try:
                    return _payload_items(candidate)
                except ContractError:
                    pass
        if values is None:
            raise ContractError("catalogo estruturado sem lista de publicacoes")
    else:
        raise ContractError("catalogo estruturado invalido")
    if not all(isinstance(item, dict) for item in values):
        raise ContractError("catalogo contem item nao estruturado")
    return list(values)


def _first(record: dict, *keys: str, default=None):
    for key in keys:
        value = record.get(key)
        if value not in (None, "", [], {}):
            return value
    return default


def parse_catalog_payload(payload: object, collection: dict) -> list[CatalogItem]:
    """Normaliza um catálogo JSON público sem depender de framework remoto."""

    result: list[CatalogItem] = []
    seen: set[str] = set()
    for raw in _payload_items(payload):
        title = str(_first(raw, "title", "name", "book_title", default="")).strip()
        author = _first(raw, "author", "authors", "contributor")
        if isinstance(author, list):
            author = author[0] if author else ""
        if isinstance(author, dict):
            author = _first(author, "name", "display_name", default="")
        author = str(author or collection.get("default_author_name", "")).strip()
        public_url = str(_first(raw, "public_url", "url", "book_url", default="")).strip()
        remote_id = str(_first(raw, "remote_id", "book_id", "id", default="")).strip()
        if not remote_id and public_url:
            remote_id = remote_id_from_url(public_url)
        if not title or not author or not remote_id or not public_url:
            raise ContractError("publicacao sem titulo, autor, id ou URL publica")
        language_original = str(
            _first(raw, "language", "lang", default=collection["language"])
        )
        language, language_path = canonical_language(language_original)
        publication_type = canonical_publication_type(
            str(_first(raw, "type", "section", "publication_type", default=collection.get("type", ""))),
            language_original,
        )
        assets_raw = _first(raw, "assets", "files", "downloads", default=[])
        if isinstance(assets_raw, dict):
            assets_raw = [
                {"format": key, "url": value}
                if isinstance(value, str)
                else {"format": key, **value}
                for key, value in assets_raw.items()
            ]
        assets: list[CatalogAsset] = []
        for asset in assets_raw or []:
            if not isinstance(asset, dict):
                continue
            publication_format = str(_first(asset, "format", "type", default="")).casefold()
            url = str(_first(asset, "url", "download_url", default=""))
            if publication_format not in {"pdf", "epub"} or not url:
                continue
            size = asset.get("size")
            assets.append(
                CatalogAsset(
                    format=publication_format,
                    url=url,
                    etag=str(asset.get("etag") or ""),
                    last_modified=str(asset.get("last_modified") or ""),
                    size=size if isinstance(size, int) and size > 0 else None,
                    remote_hash=str(asset.get("sha256") or asset.get("hash") or ""),
                )
            )
        segments_raw = raw.get("segments") or []
        segments = tuple(
            CatalogSegment(
                remote_id=str(_first(segment, "remote_id", "id", default="")),
                url=str(segment.get("url") or ""),
                order=int(_first(segment, "order", "position", default=index + 1)),
                title=str(segment.get("title") or f"Segmento {index + 1}"),
                html=str(_first(segment, "html", "content", default="")),
            )
            for index, segment in enumerate(segments_raw)
            if isinstance(segment, dict)
        )
        item = CatalogItem(
            remote_id=remote_id,
            collection_id=str(collection["id"]),
            collection_name=str(collection["name"]),
            author_name=author,
            author_key=canonical_author_key(author),
            language_original=language_original,
            language=language,
            language_path=language_path,
            publication_type=publication_type,
            title_original=title,
            title_normalized=title,
            public_url=public_url,
            edition=str(_first(raw, "edition", "version", "pub_year", default="")),
            assets=tuple(sorted(assets, key=lambda item: (item.format != "epub", item.url))),
            segments=segments,
        )
        if item.stable_key() in seen:
            continue
        seen.add(item.stable_key())
        result.append(item)
    return sorted(
        result,
        key=lambda item: (
            item.author_key,
            item.publication_type,
            item.title_normalized.casefold(),
            item.remote_id,
        ),
    )


class AcquisitionLedger:
    """Ledger local atômico; não altera metadado rastreado em simples skip."""

    def __init__(self, path: Path, now: Callable[[], str] = utc_now):
        self.path = Path(path)
        self.now = now
        self.data = self._read()

    def _read(self) -> dict:
        if not self.path.exists():
            return {"schema_version": STATE_SCHEMA, "entries": {}}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ContractError(f"ledger invalido: {self.path}: {error}") from error
        if set(value) != {"schema_version", "entries"} or value["schema_version"] != STATE_SCHEMA:
            raise ContractError("ledger com schema divergente")
        if not isinstance(value["entries"], dict):
            raise ContractError("ledger sem entries")
        return value

    def get(self, key: str) -> dict | None:
        value = self.data["entries"].get(key)
        return dict(value) if isinstance(value, dict) else None

    def transition(self, key: str, state: str, **details) -> dict:
        if state not in ALLOWED_STATES:
            raise ContractError(f"estado de aquisicao invalido: {state}")
        previous = self.data["entries"].get(key, {})
        entry = {
            **previous,
            **details,
            "state": state,
            "updated_at": self.now(),
        }
        self.data["entries"][key] = entry
        write_json_atomic(self.path, self.data)
        return dict(entry)


@dataclass(frozen=True)
class RatePolicy:
    delay_seconds: float = 2.0
    jitter_min_seconds: float = 0.5
    jitter_max_seconds: float = 1.5
    max_attempts: int = 3
    backoff_base_seconds: float = 2.0
    backoff_cap_seconds: float = 60.0
    retry_after_cap_seconds: float = 900.0

    def __post_init__(self) -> None:
        if self.delay_seconds < 2:
            raise ContractError("atraso base deve ser ao menos dois segundos")
        if not 0 <= self.jitter_min_seconds <= self.jitter_max_seconds:
            raise ContractError("jitter invalido")
        if not 1 <= self.max_attempts <= 3:
            raise ContractError("max_attempts deve estar entre 1 e 3")


class RateLimiter:
    def __init__(
        self,
        policy: RatePolicy,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
        random_uniform: Callable[[float, float], float] = random.uniform,
    ):
        self.policy = policy
        self.clock = clock
        self.sleeper = sleeper
        self.random_uniform = random_uniform
        self._last_request: float | None = None
        self._lock = threading.Lock()

    def before_request(self) -> float:
        with self._lock:
            jitter = self.random_uniform(
                self.policy.jitter_min_seconds,
                self.policy.jitter_max_seconds,
            )
            target_gap = self.policy.delay_seconds + jitter
            waited = 0.0
            if self._last_request is not None:
                waited = max(0.0, target_gap - (self.clock() - self._last_request))
                if waited:
                    self.sleeper(waited)
            self._last_request = self.clock()
            return waited

    def backoff(self, attempt: int, retry_after: str | None = None) -> float:
        delay = parse_retry_after(retry_after)
        if delay is None:
            delay = min(
                self.policy.backoff_cap_seconds,
                self.policy.backoff_base_seconds * (2 ** max(0, attempt - 1)),
            )
        delay = min(delay, self.policy.retry_after_cap_seconds)
        self.sleeper(delay)
        return delay


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    if not value:
        return None
    stripped = value.strip()
    if stripped.isdigit():
        return max(0.0, float(stripped))
    try:
        moment = parsedate_to_datetime(stripped)
    except (TypeError, ValueError, OverflowError):
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    reference = now or datetime.now(timezone.utc)
    return max(0.0, (moment - reference).total_seconds())


def contains_block_marker(text: str) -> bool:
    folded = text.casefold()
    return any(marker in folded for marker in BLOCK_MARKERS)


class _MarkdownParser(HTMLParser):
    ignored = {
        "nav",
        "header",
        "footer",
        "button",
        "script",
        "style",
        "aside",
        "form",
        "noscript",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self.buffer: list[str] = []
        self.ignore_depth = 0
        self.list_depth = 0
        self.heading: int | None = None
        self.in_pre = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self.ignored:
            self.ignore_depth += 1
            return
        if self.ignore_depth:
            return
        if re.fullmatch(r"h[1-6]", tag):
            self._flush()
            self.heading = int(tag[1])
        elif tag in {"p", "blockquote", "table", "tr", "pre"}:
            self._flush()
            self.in_pre = tag == "pre"
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
        elif tag == "li":
            self._flush()
            self.buffer.append("  " * max(0, self.list_depth - 1) + "- ")
        elif tag == "br":
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if tag in self.ignored:
            if self.ignore_depth:
                self.ignore_depth -= 1
            return
        if self.ignore_depth:
            return
        if re.fullmatch(r"h[1-6]", tag):
            self._flush()
            self.heading = None
        elif tag in {"p", "blockquote", "li", "tr", "pre"}:
            self._flush()
            self.in_pre = False
        elif tag in {"ul", "ol"}:
            self.list_depth = max(0, self.list_depth - 1)

    def handle_data(self, data: str) -> None:
        if self.ignore_depth:
            return
        value = data if self.in_pre else re.sub(r"\s+", " ", data)
        if value.strip():
            self.buffer.append(value.strip())

    def _flush(self) -> None:
        value = " ".join(self.buffer).strip()
        self.buffer.clear()
        if not value:
            return
        value = re.sub(r"\s+([,.;:!?%)\]])", r"\1", value)
        value = re.sub(r"([(\[])\s+", r"\1", value)
        if self.heading:
            value = f"{'#' * self.heading} {value}"
        self.lines.append(value)

    def markdown(self) -> str:
        self._flush()
        return "\n\n".join(self.lines).strip() + "\n"


def editorial_html_to_markdown(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError("segmento textual vazio")
    if contains_block_marker(value):
        raise ContractError("desafio anti-automacao detectado no segmento")
    parser = _MarkdownParser()
    parser.feed(value)
    parser.close()
    markdown = parser.markdown()
    if not markdown.strip():
        raise ContractError("segmento sem corpo editorial")
    return markdown


def ordered_segments(
    segments: Iterable[CatalogSegment],
    declared_count: int | None = None,
) -> list[CatalogSegment]:
    values = sorted(segments, key=lambda item: item.order)
    if not values:
        raise ContractError("publicacao sem segmentos")
    orders = [item.order for item in values]
    if len(set(orders)) != len(orders):
        raise ContractError("segmentos duplicados")
    expected = list(range(1, len(values) + 1))
    if orders != expected:
        raise ContractError("lacuna ou ordem incerta nos segmentos")
    if declared_count is not None and declared_count != len(values):
        raise ContractError("quantidade declarada diverge dos segmentos")
    if any(not item.remote_id or not item.url for item in values):
        raise ContractError("segmento sem identificador ou URL")
    return values


def _write_text_if_changed(path: Path, value: str) -> bool:
    encoded = value.encode("utf-8")
    if path.is_file() and path.read_bytes() == encoded:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return True


def write_markdown_publication(
    directory: Path,
    item: CatalogItem,
    segments: Iterable[CatalogSegment] | None = None,
    declared_count: int | None = None,
) -> tuple[list[Path], list[dict]]:
    values = ordered_segments(segments or item.segments, declared_count)
    markdown_paths: list[Path] = []
    evidence: list[dict] = []
    for segment in values:
        markdown = editorial_html_to_markdown(segment.html)
        slug = uri_slug(segment.title)
        path = Path(directory) / "text" / f"{segment.order:04d}-{slug}.md"
        _write_text_if_changed(path, markdown)
        digest = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        markdown_paths.append(path)
        evidence.append(
            {
                "remote_id": segment.remote_id,
                "url": segment.url,
                "order": segment.order,
                "title": segment.title,
                "sha256": digest,
                "path": path.relative_to(directory).as_posix(),
                "state": "completed",
            }
        )
    metadata = {
        "schema_version": "publication-text/v1",
        "remote_id": item.remote_id,
        "title": item.title_original,
        "author": item.author_name,
        "language": item.language,
        "segments": evidence,
    }
    write_json_atomic(Path(directory) / "text" / "0000-metadata.json", metadata)
    return markdown_paths, evidence


def _xhtml(title: str, body: str, language: str) -> str:
    paragraphs = []
    for block in re.split(r"\n{2,}", body.strip()):
        if block.startswith("#"):
            match = re.match(r"^(#{1,6})\s+(.*)$", block, re.S)
            if match:
                level = len(match.group(1))
                paragraphs.append(f"<h{level}>{escape(match.group(2))}</h{level}>")
                continue
        paragraphs.append(f"<p>{escape(block)}</p>")
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        f'<html xmlns="http://www.w3.org/1999/xhtml" lang="{escape(language)}">'
        f"<head><title>{escape(title)}</title></head><body>{''.join(paragraphs)}</body></html>"
    )


def generate_epub(
    target: Path,
    item: CatalogItem,
    markdown_paths: Iterable[Path],
) -> Path:
    paths = list(markdown_paths)
    if not paths:
        raise ContractError("EPUB derivado sem Markdown")
    identifier = f"urn:sha256:{item.stable_key()}"
    manifest = []
    spine = []
    navigation = []
    documents: list[tuple[str, str]] = []
    for index, path in enumerate(paths, 1):
        name = f"section-{index:04d}.xhtml"
        item_id = f"section-{index:04d}"
        title = path.stem.split("-", 1)[-1].replace("-", " ")
        content = _xhtml(title, path.read_text(encoding="utf-8"), item.language)
        documents.append((name, content))
        manifest.append(
            f'<item id="{item_id}" href="{name}" media-type="application/xhtml+xml"/>'
        )
        spine.append(f'<itemref idref="{item_id}"/>')
        navigation.append(f'<li><a href="{name}">{escape(title)}</a></li>')
    nav = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops">'
        f"<head><title>{escape(item.title_original)}</title></head>"
        f'<body><nav epub:type="toc"><ol>{"".join(navigation)}</ol></nav></body></html>'
    )
    opf = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        f'unique-identifier="pub-id" xml:lang="{escape(item.language)}">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f'<dc:identifier id="pub-id">{identifier}</dc:identifier>'
        f"<dc:title>{escape(item.title_original)}</dc:title>"
        f"<dc:creator>{escape(item.author_name)}</dc:creator>"
        f"<dc:language>{escape(item.language)}</dc:language>"
        '<meta property="dcterms:modified">2000-01-01T00:00:00Z</meta>'
        "</metadata><manifest>"
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        f'{"".join(manifest)}</manifest><spine>{"".join(spine)}</spine></package>'
    )
    container = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" '
        'media-type="application/oebps-package+xml"/></rootfiles></container>'
    )
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    with zipfile.ZipFile(temporary, "w") as archive:
        _zip_write(archive, "mimetype", b"application/epub+zip", stored=True)
        _zip_write(archive, "META-INF/container.xml", container)
        _zip_write(archive, "OEBPS/content.opf", opf)
        _zip_write(archive, "OEBPS/nav.xhtml", nav)
        for name, content in documents:
            _zip_write(archive, f"OEBPS/{name}", content)
    validate_generated_epub(temporary, expected_sections=len(paths))
    temporary.replace(target)
    return target


def _zip_write(
    archive: zipfile.ZipFile,
    name: str,
    value: str | bytes,
    *,
    stored: bool = False,
) -> None:
    info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, value.encode("utf-8") if isinstance(value, str) else value)


def validate_generated_epub(path: Path, expected_sections: int | None = None) -> None:
    if not zipfile.is_zipfile(path):
        raise ContractError("EPUB derivado nao e ZIP")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if names[0] != "mimetype" or archive.read("mimetype") != b"application/epub+zip":
            raise ContractError("EPUB derivado sem mimetype inicial")
        required = {"META-INF/container.xml", "OEBPS/content.opf", "OEBPS/nav.xhtml"}
        if not required.issubset(names):
            raise ContractError("EPUB derivado incompleto")
        sections = [name for name in names if re.fullmatch(r"OEBPS/section-\d{4}\.xhtml", name)]
        if expected_sections is not None and len(sections) != expected_sections:
            raise ContractError("EPUB derivado perdeu secoes")


def build_source_v3(
    item: CatalogItem,
    state: str,
    sources: list[dict],
    segments: list[dict] | None = None,
    derivations: list[dict] | None = None,
    history: list[dict] | None = None,
) -> dict:
    if state not in ALLOWED_STATES:
        raise ContractError(f"estado invalido: {state}")
    identity = item.publication_identity()
    return {
        "schema_version": SOURCE_SCHEMA_V3,
        "identity": {
            "remote_id": item.remote_id,
            "author_original": item.author_name,
            "author_key": item.author_key,
            "title_original": item.title_original,
            "title_normalized": item.title_normalized,
            "language_original": item.language_original,
            "language": item.language,
            "language_path": item.language_path,
            "type": item.publication_type,
            "edition": item.edition,
            "acronym": identity.acronym,
            "route_slug": identity.route_slug,
            "tags": [],
            "public_url": item.public_url,
        },
        "collection": {
            "id": item.collection_id,
            "name": item.collection_name,
        },
        "state": state,
        "sources": sorted(sources, key=lambda value: (value.get("format", ""), value.get("url", ""))),
        "segments": sorted(segments or [], key=lambda value: value.get("order", 0)),
        "derivations": sorted(derivations or [], key=lambda value: value.get("format", "")),
        "history": list(history or []),
    }
