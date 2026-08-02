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
    normalize_editorial_title,
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
    category_name: str = "Geral"
    category_path: str = "geral"
    cover_url: str = ""
    edition: str = ""
    assets: tuple[CatalogAsset, ...] = ()
    segments: tuple[CatalogSegment, ...] = ()
    local_complete: bool = False

    def __post_init__(self) -> None:
        """Canonicaliza a projeção editorial sem alterar a evidência original."""

        object.__setattr__(
            self,
            "title_normalized",
            normalize_editorial_title(self.title_normalized or self.title_original),
        )

    def publication_identity(self) -> PublicationIdentity:
        return publication_identity(
            self.author_key,
            self.language_path,
            self.publication_type,
            self.title_normalized,
            category=self.category_path,
        )

    def stable_key(self) -> str:
        material = "\0".join(
            (
                self.collection_id,
                self.remote_id,
                self.author_key,
                self.language,
                self.category_path,
                self.publication_type,
                self.title_normalized,
                self.edition,
                self.cover_url,
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
    category_name = str(collection.get("category_name") or "").strip()
    category_path = str(collection.get("category") or "").strip()
    if not category_name or not category_path or uri_slug(category_path) != category_path:
        raise ContractError("colecao sem categoria editorial oficial")
    for raw in _payload_items(payload):
        title = str(_first(raw, "title", "name", "book_title", default="")).strip()
        author = _first(raw, "author", "authors", "contributor")
        if isinstance(author, list):
            author = author[0] if author else ""
        if isinstance(author, dict):
            author = _first(author, "name", "display_name", default="")
        author = str(author or collection.get("default_author_name", "")).strip()
        public_url = str(_first(raw, "public_url", "url", "book_url", default="")).strip()
        cover_value = _first(raw, "cover_url", "cover", "cover_image", "image", default="")
        if isinstance(cover_value, dict):
            cover_value = _first(cover_value, "url", "src", default="")
        cover_url = str(cover_value or "").strip()
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
            category_name=category_name,
            category_path=category_path,
            cover_url=cover_url,
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
        attributes = dict(attrs)
        class_tokens = set(str(attributes.get("class") or "").split())
        semantic_heading = next(
            (int(token[1]) for token in class_tokens if re.fullmatch(r"h[1-6]", token)),
            None,
        )
        if re.fullmatch(r"h[1-6]", tag):
            self._flush()
            self.heading = int(tag[1])
        elif tag in {"p", "blockquote", "table", "tr", "pre"}:
            self._flush()
            self.in_pre = tag == "pre"
            if semantic_heading is not None:
                self.heading = semantic_heading
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
        elif tag == "li":
            self._flush()
            self.buffer.append("  " * max(0, self.list_depth - 1) + "- ")
        elif tag == "br":
            self._flush()
        elif tag in {"strong", "b"}:
            self.buffer.append("\x00STRONG_OPEN\x00")
        elif tag in {"em", "i"}:
            self.buffer.append("\x00EM_OPEN\x00")

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
            if tag == "p":
                self.heading = None
        elif tag in {"ul", "ol"}:
            self.list_depth = max(0, self.list_depth - 1)
        elif tag in {"strong", "b"}:
            self.buffer.append("\x00STRONG_CLOSE\x00")
        elif tag in {"em", "i"}:
            self.buffer.append("\x00EM_CLOSE\x00")

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
        value = value.replace("\x00STRONG_OPEN\x00 ", "**")
        value = value.replace(" \x00STRONG_CLOSE\x00", "**")
        value = value.replace("\x00EM_OPEN\x00 ", "*")
        value = value.replace(" \x00EM_CLOSE\x00", "*")
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


def _xhtml(
    title: str,
    body: str,
    language: str,
    *,
    page_name: str,
    running_header: str,
) -> str:
    def inline(value: str) -> str:
        escaped = escape(value)
        escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
        return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)

    paragraphs = []
    for block in re.split(r"\n{2,}", body.strip()):
        if block.startswith("#"):
            match = re.match(r"^(#{1,6})\s+(.*)$", block, re.S)
            if match:
                level = len(match.group(1))
                paragraphs.append(f"<h{level}>{inline(match.group(2))}</h{level}>")
                continue
        paragraphs.append(f"<p>{inline(block)}</p>")
    header_css = json.dumps(running_header, ensure_ascii=False)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        f'<html xmlns="http://www.w3.org/1999/xhtml" lang="{escape(language)}">'
        f'<head><title>{escape(title)}</title>'
        f'<meta name="egwsearch:running-header" content="{escape(running_header, quote=True)}"/>'
        '<meta name="egwsearch:page-chrome" content="css-page-margin-boxes"/>'
        '<style>'
        f'@page {page_name}'
        '{margin:16mm 14mm 18mm;'
        f'@top-center{{content:{header_css};font-size:.75em;color:#555}}'
        '@bottom-center{content:counter(page);font-size:.75em;color:#555}}'
        f'@page {page_name}:first{{@top-center{{content:none}}}}'
        f'body{{page:{page_name};}}'
        '</style></head>'
        f'<body epub:type="bodymatter" xmlns:epub="http://www.idpf.org/2007/ops">'
        f"{''.join(paragraphs)}</body></html>"
    )


def _abnt_access_date(value: str) -> str:
    """Formata a data efetiva de acesso sem depender de locale do sistema."""

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError("data de acesso invalida para nota de proveniencia") from error
    months = (
        "jan.", "fev.", "mar.", "abr.", "maio", "jun.",
        "jul.", "ago.", "set.", "out.", "nov.", "dez.",
    )
    return f"{parsed.day} {months[parsed.month - 1]} {parsed.year}"


def _provenance_xhtml(item: CatalogItem, accessed_at: str) -> str:
    citation_prefix = (
        f"{item.author_name.upper()}. {item.title_original}. "
        "EGW Writings, [s. d.]. Disponível em: "
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" '
        f'lang="{escape(item.language)}"><head><title>Nota de proveniência (não editorial)</title></head>'
        '<body epub:type="frontmatter acknowledgments" class="non-editorial-provenance">'
        '<h1>Nota de proveniência (não editorial)</h1>'
        '<p>Esta nota foi acrescentada pelo gerador e não integra o conteúdo editorial da obra.</p>'
        f'<p>{escape(citation_prefix)}<a href="{escape(item.public_url, quote=True)}">'
        f'&lt;{escape(item.public_url)}&gt;</a>. Acesso em: {_abnt_access_date(accessed_at)}.</p>'
        '</body></html>'
    )


def generate_epub(
    target: Path,
    item: CatalogItem,
    markdown_paths: Iterable[Path],
    cover_path: Path | None = None,
    accessed_at: str | None = None,
) -> Path:
    paths = list(markdown_paths)
    if not paths:
        raise ContractError("EPUB derivado sem Markdown")
    accessed_at = accessed_at or "2000-01-01T00:00:00+00:00"
    identifier = f"urn:sha256:{item.stable_key()}"
    cover_bytes = b""
    if cover_path is not None:
        cover_bytes = Path(cover_path).read_bytes()
        if not cover_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ContractError("capa EPUB nao e PNG")
        if len(cover_bytes) < 24:
            raise ContractError("capa EPUB PNG truncada")
    manifest = []
    spine = []
    navigation = []
    documents: list[tuple[str, str]] = []
    markdown_sources: list[tuple[str, bytes]] = []
    markdown_manifest: list[dict] = []
    for index, path in enumerate(paths, 1):
        name = f"section-{index:04d}.xhtml"
        item_id = f"section-{index:04d}"
        title = path.stem.split("-", 1)[-1].replace("-", " ")
        markdown_bytes = path.read_bytes()
        try:
            markdown = markdown_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ContractError(f"Markdown nao UTF-8: {path.name}") from error
        segment_title = (
            item.segments[index - 1].title
            if index <= len(item.segments) and item.segments[index - 1].title
            else title
        )
        content = _xhtml(
            segment_title,
            markdown,
            item.language,
            page_name=item_id,
            running_header=segment_title,
        )
        documents.append((name, content))
        markdown_sources.append((path.name, markdown_bytes))
        markdown_manifest.append(
            {
                "name": path.name,
                "order": index,
                "path": f"META-INF/egwsearch-source/{path.name}",
                "sha256": hashlib.sha256(markdown_bytes).hexdigest(),
            }
        )
        manifest.append(
            f'<item id="{item_id}" href="{name}" media-type="application/xhtml+xml"/>'
        )
        spine.append(f'<itemref idref="{item_id}"/>')
        navigation.append(f'<li><a href="{name}">{escape(segment_title)}</a></li>')
    cover_navigation = '<li><a href="cover.xhtml">Capa</a></li>' if cover_bytes else ""
    provenance_navigation = '<li><a href="provenance.xhtml">Nota de proveniência (não editorial)</a></li>'
    nav = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops">'
        f"<head><title>{escape(item.title_original)}</title></head>"
        f'<body><nav epub:type="toc"><h1>Sumário</h1><ol>{cover_navigation}{provenance_navigation}{"".join(navigation)}</ol></nav></body></html>'
    )
    cover_metadata = '<meta name="cover" content="cover-image"/>' if cover_bytes else ""
    cover_manifest = (
        '<item id="cover-image" href="cover.png" media-type="image/png" properties="cover-image"/>'
        '<item id="cover-page" href="cover.xhtml" media-type="application/xhtml+xml"/>'
        if cover_bytes
        else ""
    )
    cover_spine = '<itemref idref="cover-page"/>' if cover_bytes else ""
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
        f"{cover_metadata}"
        "</metadata><manifest>"
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        '<item id="provenance" href="provenance.xhtml" media-type="application/xhtml+xml"/>'
        f'{cover_manifest}{"".join(manifest)}</manifest><spine>{cover_spine}'
        '<itemref idref="provenance"/><itemref idref="nav"/>'
        f'{"".join(spine)}</spine></package>'
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
        _zip_write(archive, "OEBPS/provenance.xhtml", _provenance_xhtml(item, accessed_at))
        _zip_write(
            archive,
            "META-INF/egwsearch-source/manifest.json",
            json.dumps(
                {
                    "schema_version": "egwsearch-reversible-markdown/v1",
                    "files": markdown_manifest,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        for source_name, source_bytes in markdown_sources:
            _zip_write(
                archive,
                f"META-INF/egwsearch-source/{source_name}",
                source_bytes,
            )
        if cover_bytes:
            cover_width = int.from_bytes(cover_bytes[16:20], "big")
            cover_height = int.from_bytes(cover_bytes[20:24], "big")
            if cover_width < 1 or cover_height < 1:
                raise ContractError("dimensoes da capa EPUB invalidas")
            cover_xhtml = (
                '<?xml version="1.0" encoding="utf-8"?>'
                '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml" '
                'xmlns:epub="http://www.idpf.org/2007/ops" '
                f'lang="{escape(item.language)}" style="height:100%;margin:0;padding:0">'
                f'<head><title>Capa</title><meta name="viewport" content="width={cover_width},height={cover_height}"/>'
                '<style>@page{margin:0;padding:0}html,body{width:100%;height:100%;margin:0;padding:0;overflow:hidden}'
                'svg{display:block;width:100%;height:100%;margin:0;padding:0}</style></head>'
                '<body epub:type="cover">'
                '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" '
                f'viewBox="0 0 {cover_width} {cover_height}" preserveAspectRatio="xMidYMid slice" '
                f'role="img" aria-label="Capa de {escape(item.title_original)}">'
                f'<image href="cover.png" width="{cover_width}" height="{cover_height}" '
                'preserveAspectRatio="xMidYMid slice"/></svg></body></html>'
            )
            _zip_write(archive, "OEBPS/cover.png", cover_bytes)
            _zip_write(archive, "OEBPS/cover.xhtml", cover_xhtml)
        for name, content in documents:
            _zip_write(archive, f"OEBPS/{name}", content)
    validate_generated_epub(
        temporary,
        expected_sections=len(paths),
        expected_cover_sha256=(hashlib.sha256(cover_bytes).hexdigest() if cover_bytes else None),
        expected_markdown_sha256={entry["name"]: entry["sha256"] for entry in markdown_manifest},
        expected_public_url=item.public_url,
        expected_accessed_at=accessed_at,
    )
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


def validate_generated_epub(
    path: Path,
    expected_sections: int | None = None,
    expected_cover_sha256: str | None = None,
    expected_markdown_sha256: dict[str, str] | None = None,
    expected_public_url: str | None = None,
    expected_accessed_at: str | None = None,
) -> None:
    if not zipfile.is_zipfile(path):
        raise ContractError("EPUB derivado nao e ZIP")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if names[0] != "mimetype" or archive.read("mimetype") != b"application/epub+zip":
            raise ContractError("EPUB derivado sem mimetype inicial")
        required = {
            "META-INF/container.xml",
            "META-INF/egwsearch-source/manifest.json",
            "OEBPS/content.opf",
            "OEBPS/nav.xhtml",
            "OEBPS/provenance.xhtml",
        }
        if not required.issubset(names):
            raise ContractError("EPUB derivado incompleto")
        sections = [name for name in names if re.fullmatch(r"OEBPS/section-\d{4}\.xhtml", name)]
        if expected_sections is not None and len(sections) != expected_sections:
            raise ContractError("EPUB derivado perdeu secoes")
        try:
            source_manifest = json.loads(
                archive.read("META-INF/egwsearch-source/manifest.json").decode("utf-8")
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ContractError("manifesto Markdown reversivel invalido") from error
        if (
            not isinstance(source_manifest, dict)
            or set(source_manifest) != {"schema_version", "files"}
            or source_manifest["schema_version"] != "egwsearch-reversible-markdown/v1"
        ):
            raise ContractError("schema Markdown reversivel divergente")
        files = source_manifest["files"]
        if not isinstance(files, list) or len(files) != len(sections):
            raise ContractError("cardinalidade Markdown reversivel divergente")
        observed: dict[str, str] = {}
        for order, record in enumerate(files, 1):
            if not isinstance(record, dict) or set(record) != {"name", "order", "path", "sha256"}:
                raise ContractError("entrada Markdown reversivel invalida")
            name = record["name"]
            internal = record["path"]
            if (
                record["order"] != order
                or not isinstance(name, str)
                or Path(name).name != name
                or not name.endswith(".md")
                or internal != f"META-INF/egwsearch-source/{name}"
                or internal not in names
            ):
                raise ContractError("path ou ordem Markdown reversivel invalida")
            digest = hashlib.sha256(archive.read(internal)).hexdigest()
            if digest != record["sha256"]:
                raise ContractError("hash Markdown reversivel divergente")
            observed[name] = digest
        internal_markdown = {
            name
            for name in names
            if name.startswith("META-INF/egwsearch-source/") and name.endswith(".md")
        }
        if internal_markdown != {record["path"] for record in files}:
            raise ContractError("EPUB contem Markdown reversivel nao manifestado")
        if expected_markdown_sha256 is not None and observed != expected_markdown_sha256:
            raise ContractError("fonte Markdown EPUB diverge da esperada")
        opf = archive.read("OEBPS/content.opf").decode("utf-8")
        provenance = archive.read("OEBPS/provenance.xhtml").decode("utf-8")
        if (
            "Nota de proveniência (não editorial)" not in provenance
            or 'epub:type="frontmatter acknowledgments"' not in provenance
        ):
            raise ContractError("nota nao editorial inicial ausente")
        provenance_position = opf.find('idref="provenance"')
        nav_position = opf.find('idref="nav"')
        first_section_position = opf.find('idref="section-0001"')
        if not (0 <= provenance_position < nav_position < first_section_position):
            raise ContractError("proveniencia e sumario fora da ordem inicial")
        if expected_public_url is not None and f'href="{escape(expected_public_url, quote=True)}"' not in provenance:
            raise ContractError("nota nao editorial sem URL oficial")
        if expected_accessed_at is not None and _abnt_access_date(expected_accessed_at) not in provenance:
            raise ContractError("nota nao editorial sem data de acesso")
        for section_name in sections:
            section = archive.read(section_name).decode("utf-8")
            section_id = Path(section_name).stem
            body_match = re.search(r"<body\b[^>]*>(.*?)</body>", section, re.DOTALL)
            if (
                body_match is None
                or '<meta name="egwsearch:running-header"' not in section
                or '<meta name="egwsearch:page-chrome" content="css-page-margin-boxes"/>' not in section
                or f"@page {section_id}" not in section
                or "@top-center{content:" not in section
                or "@bottom-center{content:counter(page)" not in section
                or f"@page {section_id}:first{{@top-center{{content:none}}}}" not in section
                or re.search(r"<(?:header|footer)\b", body_match.group(1))
            ):
                raise ContractError("cabecalho ou rodape paginado divergente")
        if expected_cover_sha256 is not None:
            if not {"OEBPS/cover.png", "OEBPS/cover.xhtml"}.issubset(names):
                raise ContractError("EPUB derivado sem capa")
            if hashlib.sha256(archive.read("OEBPS/cover.png")).hexdigest() != expected_cover_sha256:
                raise ContractError("EPUB derivado diverge de cover.png")
            if 'properties="cover-image"' not in opf:
                raise ContractError("EPUB derivado sem propriedade cover-image")
            if not (0 <= opf.find('idref="cover-page"') < opf.find('idref="section-0001"')):
                raise ContractError("pagina de capa nao inicia o spine EPUB")
            cover_page = archive.read("OEBPS/cover.xhtml").decode("utf-8")
            cover_body = re.search(r"<body\b[^>]*>(.*?)</body>", cover_page, re.DOTALL)
            if (
                cover_body is None
                or not re.fullmatch(r"<svg\b.*</svg>", cover_body.group(1), re.DOTALL)
                or 'epub:type="cover"' not in cover_page
                or '@page{margin:0;padding:0}' not in cover_page
                or 'html,body{width:100%;height:100%;margin:0;padding:0;overflow:hidden}' not in cover_page
                or '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"' not in cover_page
                or 'preserveAspectRatio="xMidYMid slice"' not in cover_page
                or re.search(r"<(?:p|h[1-6]|div|span|img|text)\b", cover_body.group(1))
            ):
                raise ContractError("pagina de capa EPUB nao e exclusiva e borda a borda")


def restore_markdown_from_epub(epub_path: Path, target_directory: Path) -> list[Path]:
    """Restaura exatamente o payload Markdown manifestado dentro do EPUB."""

    target = Path(target_directory)
    target.mkdir(parents=True, exist_ok=True)
    restored: list[Path] = []
    with zipfile.ZipFile(epub_path) as archive:
        try:
            manifest = json.loads(
                archive.read("META-INF/egwsearch-source/manifest.json").decode("utf-8")
            )
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ContractError("manifesto Markdown reversivel invalido") from error
        files = manifest.get("files") if isinstance(manifest, dict) else None
        if (
            not isinstance(manifest, dict)
            or manifest.get("schema_version") != "egwsearch-reversible-markdown/v1"
            or not isinstance(files, list)
        ):
            raise ContractError("schema Markdown reversivel divergente")
        for order, record in enumerate(files, 1):
            if not isinstance(record, dict):
                raise ContractError("entrada Markdown reversivel invalida")
            name = record.get("name")
            internal = record.get("path")
            if (
                record.get("order") != order
                or not isinstance(name, str)
                or Path(name).name != name
                or not name.endswith(".md")
                or internal != f"META-INF/egwsearch-source/{name}"
            ):
                raise ContractError("path ou ordem Markdown reversivel invalida")
            try:
                value = archive.read(internal)
            except KeyError as error:
                raise ContractError("Markdown reversivel ausente") from error
            if hashlib.sha256(value).hexdigest() != record.get("sha256"):
                raise ContractError("hash Markdown reversivel divergente")
            destination = target / name
            temporary = destination.with_name(f".{destination.name}.tmp")
            temporary.write_bytes(value)
            temporary.replace(destination)
            restored.append(destination)
    return restored


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
            "category_original": item.category_name,
            "category": item.category_path,
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
            "category_original": item.category_name,
            "category": item.category_path,
        },
        "state": state,
        "sources": sorted(sources, key=lambda value: (value.get("format", ""), value.get("url", ""))),
        "segments": sorted(segments or [], key=lambda value: value.get("order", 0)),
        "derivations": sorted(derivations or [], key=lambda value: value.get("format", "")),
        "history": list(history or []),
    }
