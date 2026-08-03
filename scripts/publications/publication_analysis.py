# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Executa experimentos de chunking em EPUB/PDF sem persistir o corpus.

A capacidade constrói uma referência textual efêmera, executa segmentadores
locais reais, mede sua fidelidade e grava somente métricas e hashes de prova.
Conhecimento repetível fica no catálogo/base global; texto editorial nunca é
persistido no manifesto.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import statistics
import sys
import time
from typing import Iterable
from xml.etree import ElementTree
import zipfile

from publication_contract import (
    ContractError,
    DEFAULT_CONFIG_PATH,
    REPOSITORY_ROOT,
    hash_file,
    load_config,
    resolve_repository_path,
    runtime_paths,
    validate_file_signature,
    write_json_atomic,
)
from acquisition import AcquisitionLedger
from publication_console import PublicationReporter


MANIFEST_SCHEMA = "publication-chunking-analysis/v2"
LEARNING_SCHEMA = "publication-chunking-learning/v1"
CATALOG_SCHEMA = "publication-chunking-method-catalog/v1"
ANALYZER_ID = "egwSearch/publication_analysis.py"
ANALYZER_VERSION = "2"
CATALOG_PATH = REPOSITORY_ROOT / "config" / "publication-chunking-methods.json"
MAX_ZIP_ENTRIES = 10_000
MAX_ZIP_EXPANDED = 512 * 1024 * 1024
MAX_XML_BYTES = 16 * 1024 * 1024
MAX_EPUB_TEXT_BYTES = 128 * 1024 * 1024
MAX_PDF_TEXT_BYTES = 128 * 1024 * 1024
MAX_EXPERIMENT_CHUNKS = 250_000
FRESHNESS_WINDOW = timedelta(hours=24)


class AnalysisError(ContractError):
    """Representa ativo ou manifesto que não pode ser analisado com segurança."""


def manifest_path_for(asset: Path) -> Path:
    """Mantém relação inequívoca entre um ativo e seu manifesto derivado."""

    return asset.with_name(f"{asset.name}.chunking.json")


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _fingerprint(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _write_json_if_changed(path: Path, document: dict) -> bool:
    payload = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if path.is_file() and path.read_bytes() == payload:
        return False
    write_json_atomic(path, document)
    return True


def _effective_now(now: datetime | None = None) -> datetime:
    """Normaliza o relógio injetável usado pela prova temporal."""

    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        raise AnalysisError("relógio de análise sem fuso horário")
    return value.astimezone(timezone.utc)


def _successful_age(document: dict, now: datetime) -> timedelta | None:
    """Retorna a idade somente de uma conclusão temporal íntegra."""

    execution = document.get("execution")
    if not isinstance(execution, dict) or execution.get("status") != "completed":
        return None
    completed_at = execution.get("completed_at")
    if not isinstance(completed_at, str):
        return None
    try:
        completed = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    if completed.tzinfo is None:
        return None
    age = now - completed.astimezone(timezone.utc)
    return age if age >= timedelta(0) else None


def _current_manifest(
    target: Path,
    evidence,
    catalog_hash: str,
    metadata_path: Path | None,
) -> dict | None:
    """Valida identidade, configuração e contexto antes de qualquer reuso."""

    if not target.is_file():
        return None
    try:
        current = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    asset_state = current.get("asset") if isinstance(current, dict) else None
    generator = current.get("generator") if isinstance(current, dict) else None
    current_catalog = current.get("catalog") if isinstance(current, dict) else None
    metadata_current = (
        metadata_path is None
        or target.stat().st_mtime_ns >= metadata_path.stat().st_mtime_ns
    )
    if not (
        isinstance(current, dict)
        and current.get("schema_version") == MANIFEST_SCHEMA
        and isinstance(generator, dict)
        and generator.get("id") == ANALYZER_ID
        and generator.get("version") == ANALYZER_VERSION
        and isinstance(current_catalog, dict)
        and current_catalog.get("sha256") == catalog_hash
        and isinstance(asset_state, dict)
        and asset_state.get("size") == evidence.size
        and asset_state.get("hashes") == evidence.as_dict()
        and metadata_current
    ):
        return None
    return current


def _safe_zip_entries(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    infos = archive.infolist()
    if not infos or len(infos) > MAX_ZIP_ENTRIES:
        raise AnalysisError("EPUB excede cardinalidade segura de entradas")
    expanded = 0
    safe_infos = []
    for info in infos:
        name = info.filename
        # Alguns EPUBs publicados pela origem contêm um registro ZIP vazio.
        # Ele não designa arquivo, não é lido nem extraído e pode ser ignorado
        # sem relaxar a proteção contra caminhos absolutos ou traversal.
        if not name:
            continue
        path = PurePosixPath(name)
        if (
            "\\" in name
            or path.is_absolute()
            or ".." in path.parts
            or len(name) > 512
        ):
            raise AnalysisError(f"EPUB contém path interno inseguro: {name!r}")
        expanded += info.file_size
        if expanded > MAX_ZIP_EXPANDED:
            raise AnalysisError("EPUB excede tamanho expandido seguro")
        if info.compress_size and info.file_size / info.compress_size > 200:
            raise AnalysisError("EPUB excede razão segura de expansão")
        safe_infos.append(info)
    if not safe_infos:
        raise AnalysisError("EPUB não contém entradas utilizáveis")
    return safe_infos


def _xml(archive: zipfile.ZipFile, name: str) -> ElementTree.Element:
    try:
        info = archive.getinfo(name)
        if info.file_size > MAX_XML_BYTES:
            raise AnalysisError(f"XML interno excede limite: {name}")
        payload = archive.read(info)
        return ElementTree.fromstring(payload)
    except (KeyError, zipfile.BadZipFile, ElementTree.ParseError) as error:
        raise AnalysisError(f"XML interno inválido: {name}") from error


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def _attribute_local(element: ElementTree.Element, name: str) -> str:
    for key, value in element.attrib.items():
        if key.rsplit("}", 1)[-1].casefold() == name.casefold():
            return str(value)
    return ""


def _sentence_count(text: str) -> int:
    return len(
        [
            part
            for part in re.split(r"(?<=[.!?…])\s+(?=[\w\"“‘(])", text.strip())
            if part.strip()
        ]
    )


def _normalize_text(text: str) -> str:
    """Normaliza somente espaço e Unicode implícito, sem reescrever palavras."""

    return " ".join(text.replace("\u00ad", "").split())


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", _normalize_text(text).casefold(), re.UNICODE)


def _token_hash(tokens: Iterable[str]) -> str:
    return hashlib.sha256("\0".join(tokens).encode("utf-8")).hexdigest()


def _catalog() -> tuple[dict, str]:
    try:
        document = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AnalysisError(f"catálogo global de métodos inválido: {error}") from error
    if (
        not isinstance(document, dict)
        or document.get("schema_version") != CATALOG_SCHEMA
        or not isinstance(document.get("methods"), list)
    ):
        raise AnalysisError("catálogo global de métodos incompatível")
    identifiers = [entry.get("id") for entry in document["methods"] if isinstance(entry, dict)]
    if len(identifiers) != len(set(identifiers)) or not all(isinstance(value, str) for value in identifiers):
        raise AnalysisError("catálogo global de métodos possui IDs inválidos")
    return document, _fingerprint(document)


def learning_path_for(source_root: Path) -> Path:
    return source_root.resolve() / "chunking-learning.json"


def _line_signature(text: str) -> str:
    value = _normalize_text(text).casefold()
    value = re.sub(r"\d+", "#", value)
    return re.sub(r"[^\w#]+", " ", value, flags=re.UNICODE).strip()


def _looks_like_heading(text: str) -> bool:
    value = _normalize_text(text)
    return bool(
        2 <= len(value) <= 120
        and len(value.split()) <= 18
        and (
            value.isupper()
            or re.match(
                r"^(?:chapter|cap[ií]tulo|day|dia|article|artigo|section|se[cç][aã]o)\b",
                value,
                re.IGNORECASE,
            )
        )
    )


def _sentences(text: str) -> list[str]:
    return [
        _normalize_text(part)
        for part in re.split(r"(?<=[.!?…])\s+(?=[\w\"“‘(])", _normalize_text(text))
        if _normalize_text(part)
    ]


def _boundary_positions(units: Iterable[str]) -> list[int]:
    positions: list[int] = []
    total = 0
    values = list(units)
    for unit in values[:-1]:
        total += len(_tokens(unit))
        positions.append(total)
    return positions


def _reference_model(blocks: list[dict], pages: list[list[str]], *, complete: bool, noise: list[dict], cross_page: list[dict]) -> dict:
    paragraphs = [_normalize_text(block["text"]) for block in blocks if block.get("kind") != "heading" and _normalize_text(block.get("text", ""))]
    headings = [_normalize_text(block["text"]) for block in blocks if block.get("kind") == "heading" and _normalize_text(block.get("text", ""))]
    ordered = [_normalize_text(block.get("text", "")) for block in blocks if _normalize_text(block.get("text", ""))]
    text = "\n\n".join(ordered)
    sentences = _sentences(text)
    page_texts = ["\n\n".join(_normalize_text(value) for value in page if _normalize_text(value)) for page in pages]
    tokens = _tokens(text)
    return {
        "text": text,
        "tokens": tokens,
        "blocks": blocks,
        "paragraphs": ordered,
        "body_paragraphs": paragraphs,
        "headings": headings,
        "sentences": sentences,
        "pages": page_texts,
        "complete": complete,
        "noise": noise,
        "cross_page": cross_page,
        "boundaries": {
            "paragraph": _boundary_positions(ordered),
            "sentence": _boundary_positions(sentences),
            "page": _boundary_positions(page_texts),
        },
    }


def _epub_report(asset: Path) -> dict:
    validate_file_signature(asset, "epub")
    with zipfile.ZipFile(asset) as archive:
        infos = _safe_zip_entries(archive)
        names = {info.filename for info in infos}
        container = _xml(archive, "META-INF/container.xml")
        rootfiles = [
            _attribute_local(element, "full-path")
            for element in container.iter()
            if _local_name(element.tag) == "rootfile"
        ]
        rootfiles = [value for value in rootfiles if value]
        if len(rootfiles) != 1 or rootfiles[0] not in names:
            raise AnalysisError("EPUB sem pacote OCF inequívoco")
        package_path = rootfiles[0]
        package = _xml(archive, package_path)
        package_dir = PurePosixPath(package_path).parent
        manifest: dict[str, dict] = {}
        spine: list[str] = []
        metadata = {"title": "", "creator": "", "language": ""}
        for element in package.iter():
            local = _local_name(element.tag)
            if local == "item":
                identifier = str(element.attrib.get("id") or "")
                href = str(element.attrib.get("href") or "")
                if identifier and href:
                    resolved = (package_dir / href).as_posix()
                    if ".." in PurePosixPath(resolved).parts or resolved not in names:
                        raise AnalysisError("manifesto EPUB referencia path ausente")
                    manifest[identifier] = {
                        "path": resolved,
                        "media_type": str(element.attrib.get("media-type") or ""),
                        "properties": str(element.attrib.get("properties") or ""),
                    }
            elif local == "itemref":
                identifier = str(element.attrib.get("idref") or "")
                if identifier:
                    spine.append(identifier)
            elif local in metadata and not metadata[local]:
                metadata[local] = " ".join("".join(element.itertext()).split())

        content_paths = [
            manifest[identifier]["path"]
            for identifier in spine
            if identifier in manifest
            and manifest[identifier]["media_type"]
            in {"application/xhtml+xml", "text/html"}
        ]
        if not content_paths:
            raise AnalysisError("EPUB sem conteúdo XHTML no spine")

        counts: Counter[str] = Counter()
        heading_levels: Counter[str] = Counter()
        title_samples: list[str] = []
        blocks: list[dict] = []
        pages: list[list[str]] = []
        total_text_bytes = 0
        for content_path in content_paths:
            root = _xml(archive, content_path)
            root_type = " ".join(
                _attribute_local(element, "type")
                for element in root.iter()
                if _local_name(element.tag) in {"html", "body"}
            ).casefold()
            internal_name = PurePosixPath(content_path).name.casefold()
            if (
                {"cover", "frontmatter", "toc"} & set(root_type.split())
                or internal_name in {"cover.xhtml", "provenance.xhtml", "nav.xhtml", "toc.xhtml"}
            ):
                counts["non_editorial_spine_documents"] += 1
                continue
            text = " ".join("".join(root.itertext()).split())
            total_text_bytes += len(text.encode("utf-8"))
            if total_text_bytes > MAX_EPUB_TEXT_BYTES:
                raise AnalysisError("EPUB excede limite de texto analisável")
            counts["words"] += len(re.findall(r"\b\w+\b", text, re.UNICODE))
            counts["sentences"] += _sentence_count(text)
            document_blocks: list[str] = []
            for element in root.iter():
                local = _local_name(element.tag)
                if local in {"p", "li", "blockquote", "td"}:
                    value = _normalize_text("".join(element.itertext()))
                    if value:
                        counts["paragraphs"] += 1
                        blocks.append(
                            {
                                "kind": "paragraph",
                                "text": value,
                                "document": len(pages),
                            }
                        )
                        document_blocks.append(value)
                if re.fullmatch(r"h[1-6]", local):
                    value = _normalize_text("".join(element.itertext()))
                    if value:
                        counts["headings"] += 1
                        heading_levels[local] += 1
                        blocks.append(
                            {
                                "kind": "heading",
                                "text": value,
                                "level": int(local[1]),
                                "document": len(pages),
                            }
                        )
                        document_blocks.append(value)
                        if len(title_samples) < 128:
                            title_samples.append(value)
                if local in {"section", "article"}:
                    counts[local] += 1
                epub_type = _attribute_local(element, "type").casefold()
                if "pagebreak" in epub_type or _attribute_local(element, "role") == "doc-pagebreak":
                    counts["pagebreaks"] += 1
            if document_blocks:
                pages.append(document_blocks)
        counts["spine_documents"] = len(content_paths)
        counts["nav_documents"] = sum(
            1 for value in manifest.values() if "nav" in value["properties"].split()
        )
        counts["ncx_documents"] = sum(
            1
            for value in manifest.values()
            if value["media_type"] == "application/x-dtbncx+xml"
        )
        counts["embedded_markdown_files"] = sum(
            1
            for name in names
            if name.startswith("META-INF/egwsearch-source/") and name.endswith(".md")
        )
        counts["reversible_manifest"] = int(
            "META-INF/egwsearch-source/manifest.json" in names
        )
        joined_titles = "\n".join(title_samples)
        counts["date_like_headings"] = len(
            re.findall(
                r"\b(?:[0-3]?\d\s+(?:de\s+)?[A-Za-zÀ-ÿ]+|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+[0-3]?\d)\b",
                joined_titles,
                re.IGNORECASE,
            )
        )
        model = _reference_model(
            blocks,
            pages,
            complete=True,
            noise=[],
            cross_page=[],
        )
        return {
            "parser": {
                "selected": "python-stdlib/zipfile+xml.etree",
                "attempts": [
                    {"id": "python-stdlib/zipfile+xml.etree", "status": "passed"}
                ],
            },
            "metadata_evidence": metadata,
            "structure": {
                **dict(sorted(counts.items())),
                "heading_levels": dict(sorted(heading_levels.items())),
            },
            "limitations": [],
            "_model": model,
        }


def _epub_structural_fallback(asset: Path, error: AnalysisError) -> dict:
    """Registra EPUB malformado sem ler nem extrair entradas não confiáveis."""

    with zipfile.ZipFile(asset) as archive:
        infos = archive.infolist()
        structure = {
            "zip_entries": len(infos),
            "named_zip_entries": sum(bool(info.filename) for info in infos),
            "empty_zip_entries": sum(not info.filename for info in infos),
            "expanded_bytes_declared": sum(max(0, info.file_size) for info in infos),
        }
    return {
        "parser": {
            "selected": "binary-epub-structure",
            "attempts": [
                {
                    "id": "python-stdlib/zipfile+xml.etree",
                    "status": "failed",
                    "error": type(error).__name__,
                },
                {"id": "binary-epub-structure", "status": "passed-structural-only"},
            ],
        },
        "metadata_evidence": {},
        "structure": structure,
        "limitations": [f"epub-content-unavailable:{error}"],
        "_model": _reference_model([], [], complete=False, noise=[], cross_page=[]),
    }


def _distributed_indices(total: int, maximum: int) -> list[int]:
    if total <= maximum:
        return list(range(total))
    return sorted({round(index * (total - 1) / (maximum - 1)) for index in range(maximum)})


def extract_metadata_evidence(asset: Path) -> dict:
    """Extrai somente título/autoria/idioma para migração de metadado legado."""

    suffix = asset.suffix.casefold()
    if suffix == ".pdf":
        validate_file_signature(asset, "pdf")
        try:
            import pypdfium2 as pdfium

            document = pdfium.PdfDocument(str(asset))
            try:
                raw = document.get_metadata_dict() or {}
            finally:
                document.close()
            return {
                "title": str(raw.get("Title") or "").strip(),
                "creator": str(raw.get("Author") or "").strip(),
                "language": "",
            }
        except Exception:
            return {"title": "", "creator": "", "language": ""}
    if suffix != ".epub":
        raise AnalysisError(f"formato sem metadado editorial: {asset.name}")
    validate_file_signature(asset, "epub")
    with zipfile.ZipFile(asset) as archive:
        names = {info.filename for info in _safe_zip_entries(archive)}
        container = _xml(archive, "META-INF/container.xml")
        rootfiles = [
            _attribute_local(element, "full-path")
            for element in container.iter()
            if _local_name(element.tag) == "rootfile"
        ]
        rootfiles = [value for value in rootfiles if value]
        if len(rootfiles) != 1 or rootfiles[0] not in names:
            raise AnalysisError("EPUB sem pacote OCF inequívoco")
        package = _xml(archive, rootfiles[0])
        metadata = {"title": "", "creator": "", "language": ""}
        for element in package.iter():
            local = _local_name(element.tag)
            if local in metadata and not metadata[local]:
                metadata[local] = " ".join("".join(element.itertext()).split())
        return metadata


def _pdf_report(asset: Path) -> dict:
    validate_file_signature(asset, "pdf")
    limitations: list[str] = []
    try:
        import pypdfium2 as pdfium

        document = pdfium.PdfDocument(str(asset))
        try:
            raw_metadata = document.get_metadata_dict() or {}
            metadata = {
                "title": str(raw_metadata.get("Title") or "").strip(),
                "creator": str(raw_metadata.get("Author") or "").strip(),
                "language": "",
            }
            pages = len(document)
            raw_pages: list[list[str]] = []
            total_text_bytes = 0
            for index in range(pages):
                page = document[index]
                try:
                    textpage = page.get_textpage()
                    try:
                        text = textpage.get_text_range()
                    finally:
                        textpage.close()
                finally:
                    page.close()
                total_text_bytes += len(text.encode("utf-8", errors="replace"))
                if total_text_bytes > MAX_PDF_TEXT_BYTES:
                    raise AnalysisError("PDF excede limite integral de texto analisável")
                raw_pages.append([line.rstrip() for line in text.splitlines()])
        finally:
            document.close()

        positional: Counter[tuple[str, int]] = Counter()
        for lines in raw_pages:
            nonempty = [line for line in lines if _normalize_text(line)]
            for position, line in enumerate(nonempty[:3]):
                signature = _line_signature(line)
                if signature:
                    positional[(signature, position)] += 1
            for offset, line in enumerate(reversed(nonempty[-3:]), 1):
                signature = _line_signature(line)
                if signature:
                    positional[(signature, -offset)] += 1
        threshold = max(3, math.ceil(max(1, len(raw_pages)) * 0.6))
        repeated = {
            key for key, count in positional.items() if count >= threshold and len(key[0]) >= 2
        }
        noise_counter: Counter[tuple[str, int]] = Counter()
        clean_pages: list[list[str]] = []
        for lines in raw_pages:
            nonempty_positions = [index for index, line in enumerate(lines) if _normalize_text(line)]
            position_map: dict[int, int] = {}
            for position, line_index in enumerate(nonempty_positions[:3]):
                position_map[line_index] = position
            for offset, line_index in enumerate(reversed(nonempty_positions[-3:]), 1):
                position_map[line_index] = -offset
            cleaned: list[str] = []
            for line_index, line in enumerate(lines):
                value = _normalize_text(line)
                signature = _line_signature(value)
                positional_key = (signature, position_map.get(line_index, 99))
                is_page_number = bool(
                    value
                    and position_map.get(line_index) in {0, 1, 2, -1, -2, -3}
                    and re.fullmatch(r"(?:\d+|[ivxlcdm]+)", value, re.IGNORECASE)
                )
                if value and (positional_key in repeated or is_page_number):
                    noise_counter[positional_key] += 1
                    continue
                cleaned.append(line.rstrip())
            clean_pages.append(cleaned)

        page_blocks: list[list[str]] = []
        for lines in clean_pages:
            groups: list[list[str]] = []
            current: list[str] = []
            for line in lines:
                value = _normalize_text(line)
                if not value:
                    if current:
                        groups.append(current)
                        current = []
                    continue
                if _looks_like_heading(value):
                    if current:
                        groups.append(current)
                        current = []
                    groups.append([value])
                else:
                    current.append(value)
            if current:
                groups.append(current)
            normalized_groups: list[str] = []
            for group in groups:
                merged = ""
                for line in group:
                    if merged.endswith("-") and line[:1].islower():
                        merged = merged[:-1] + line
                    else:
                        merged = f"{merged} {line}".strip()
                if merged:
                    normalized_groups.append(merged)
            page_blocks.append(normalized_groups)

        cross_page: list[dict] = []
        for index in range(len(page_blocks) - 1):
            left = page_blocks[index]
            right = page_blocks[index + 1]
            if not left or not right:
                continue
            tail = left[-1].rstrip()
            head = right[0].lstrip()
            continuation = bool(
                tail
                and head
                and (
                    tail.endswith("-")
                    or (
                        not re.search(r"[.!?…:\"”’)]$", tail)
                        and (head[:1].islower() or head[:1] in {",", ";", ":"})
                    )
                )
            )
            if continuation:
                if tail.endswith("-") and head[:1].islower():
                    joined = tail[:-1] + head
                else:
                    joined = f"{tail} {head}"
                left[-1] = joined
                right.pop(0)
                cross_page.append(
                    {
                        "from": index + 1,
                        "to": index + 2,
                        "proof": _fingerprint({"tail": _token_hash(_tokens(tail)), "head": _token_hash(_tokens(head))}),
                    }
                )

        blocks: list[dict] = []
        for page_index, values in enumerate(page_blocks):
            for value in values:
                blocks.append(
                    {
                        "kind": "heading" if _looks_like_heading(value) else "paragraph",
                        "text": value,
                        "page": page_index + 1,
                    }
                )
        noise = [
            {
                "signature": _fingerprint({"pattern": signature, "position": position}),
                "position": position,
                "occurrences": count,
            }
            for (signature, position), count in sorted(noise_counter.items())
        ]
        model = _reference_model(
            blocks,
            page_blocks,
            complete=True,
            noise=noise,
            cross_page=cross_page,
        )
        words = len(re.findall(r"\b\w+\b", model["text"], re.UNICODE))
        sentences = len(model["sentences"])
        paragraphs = len(model["paragraphs"])
        heading_candidates = len(model["headings"])
        structure = {
            "pages": pages,
            "analyzed_pages": len(raw_pages),
            "coverage_ppm": 1_000_000 if len(raw_pages) == pages else 0,
            "words": words,
            "sentences": sentences,
            "paragraphs": paragraphs,
            "heading_candidates": heading_candidates,
            "noise_patterns": len(noise),
            "noise_occurrences": sum(entry["occurrences"] for entry in noise),
            "cross_page_continuations": len(cross_page),
        }
        return {
            "parser": {
                "selected": "pypdfium2",
                "attempts": [{"id": "pypdfium2", "status": "passed"}],
            },
            "metadata_evidence": metadata,
            "structure": structure,
            "limitations": limitations + ([] if words else ["text-layer-empty"]),
            "_model": model,
        }
    except Exception as error:
        payload = asset.read_bytes()
        pages = len(re.findall(rb"/Type\s*/Page\b", payload))
        return {
            "parser": {
                "selected": "binary-pdf-structure",
                "attempts": [
                    {"id": "pypdfium2", "status": "failed", "error": type(error).__name__},
                    {"id": "binary-pdf-structure", "status": "passed-structural-only"},
                ],
            },
            "metadata_evidence": {},
            "structure": {"pages_approximate": pages},
            "limitations": ["text-unavailable-binary-fallback"],
            "_model": _reference_model([], [], complete=False, noise=[], cross_page=[]),
        }


def inspect_asset(asset: Path, evidence=None) -> dict:
    """Inspeciona o ativo uma vez e retorna somente sinais estruturais."""

    suffix = asset.suffix.casefold()
    if suffix == ".epub":
        publication_format = "epub"
        try:
            report = _epub_report(asset)
        except AnalysisError as error:
            report = _epub_structural_fallback(asset, error)
    elif suffix == ".pdf":
        publication_format = "pdf"
        report = _pdf_report(asset)
    else:
        raise AnalysisError(f"formato não analisável: {asset.name}")
    evidence = evidence or hash_file(asset)
    structural_fingerprint = {
        "format": publication_format,
        "parser": report["parser"]["selected"],
        "structure": report["structure"],
    }
    return {
        "format": publication_format,
        "size": evidence.size,
        "hashes": evidence.as_dict(),
        **report,
        "fingerprint": _fingerprint(structural_fingerprint),
    }


def _pack_units(units: list[str], maximum_words: int) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    words = 0
    for unit in units:
        size = len(re.findall(r"\b\w+\b", unit, re.UNICODE))
        if current and words + size > maximum_words:
            chunks.append("\n\n".join(current))
            current = []
            words = 0
        current.append(unit)
        words += size
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _heading_chunks(model: dict) -> list[str]:
    chunks: list[list[str]] = []
    current: list[str] = []
    for block in model["blocks"]:
        value = _normalize_text(block.get("text", ""))
        if not value:
            continue
        if block.get("kind") == "heading" and current:
            chunks.append(current)
            current = []
        current.append(value)
    if current:
        chunks.append(current)
    return ["\n\n".join(value) for value in chunks]


def _editorial_chunks(model: dict, publication_type: str) -> tuple[list[str], dict] | None:
    headings = [block for block in model["blocks"] if block.get("kind") == "heading"]
    if not headings:
        return None
    is_devotional = publication_type in {"devocionais", "devotionals"}
    is_periodical = publication_type in {"periodicos", "periodicals"}
    date_pattern = re.compile(
        r"\b(?:[0-3]?\d\s+(?:de\s+)?[A-Za-zÀ-ÿ]+|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+[0-3]?\d)\b",
        re.IGNORECASE,
    )
    if is_devotional and not any(date_pattern.search(block["text"]) for block in headings):
        return None
    if not is_devotional and not is_periodical:
        return None
    return _heading_chunks(model), {
        "unit": "day" if is_devotional else "article",
        "boundary_source": "heading-regex+publication-type",
    }


def _candidate_runs(report: dict, context: dict) -> list[tuple[str, list[str], dict, str | None]]:
    model = report["_model"]
    if not model["complete"] or not model["tokens"]:
        return []
    runs: list[tuple[str, list[str], dict, str | None]] = []
    text = model["text"]
    token_values = model["tokens"]
    fixed_size = 220
    runs.append(
        (
            "fixed-window",
            [" ".join(token_values[index : index + fixed_size]) for index in range(0, len(token_values), fixed_size)],
            {"tokens": fixed_size, "overlap": 0},
            None,
        )
    )
    runs.append(
        (
            "recursive-separator",
            _pack_units(model["paragraphs"], 450),
            {"maximum_words": 450, "separators": ["paragraph", "sentence", "token"]},
            "paragraph",
        )
    )
    runs.append(("sentence", list(model["sentences"]), {"boundary": "punctuation-regex-v1"}, "sentence"))
    runs.append(
        (
            "sentence-window",
            [" ".join(model["sentences"][index : index + 6]) for index in range(0, len(model["sentences"]), 6)],
            {"sentences": 6, "overlap": 0, "boundary": "punctuation-regex-v1"},
            "sentence",
        )
    )
    runs.append(("paragraph", list(model["paragraphs"]), {"boundary": "parsed-block"}, "paragraph"))
    if model["headings"]:
        heading_pattern = r"^(?:" + "|".join(
            re.escape(value) for value in model["headings"][:64]
        ) + r")$"
        matches = list(re.finditer(heading_pattern, text, flags=re.MULTILINE))
        regex_chunks: list[str] = []
        if matches and matches[0].start():
            regex_chunks.append(text[: matches[0].start()])
        regex_chunks.extend(
            text[match.start() : (matches[index + 1].start() if index + 1 < len(matches) else len(text))]
            for index, match in enumerate(matches)
        )
        runs.append(
            (
                "regex-structural",
                regex_chunks,
                {"pattern_sha256": hashlib.sha256(heading_pattern.encode("utf-8")).hexdigest(), "flags": ["MULTILINE"]},
                "heading",
            )
        )
        runs.append(
            (
                "hierarchical-structure",
                _heading_chunks(model),
                {"boundary": "parsed-heading", "preserve_order": True},
                "heading",
            )
        )
    editorial = _editorial_chunks(model, str(context.get("type") or "").casefold())
    if editorial is not None:
        chunks, parameters = editorial
        runs.append(("editorial-unit", chunks, parameters, "heading"))
    # EPUB só poderá testar página quando o modelo representar a page-list e
    # cada pagebreak, não meramente documentos do spine.
    if report["format"] == "pdf":
        runs.append(("page-layout", list(model["pages"]), {"boundary": "physical-page"}, "page"))
    runs.append(("whole-document", [text], {"boundary": "none"}, "document"))
    return [entry for entry in runs if entry[1] and len(entry[1]) <= MAX_EXPERIMENT_CHUNKS]


def _measure_experiment(
    method: str,
    chunks: list[str],
    parameters: dict,
    boundary_kind: str | None,
    model: dict,
) -> dict:
    started = time.perf_counter_ns()
    reference_tokens = model["tokens"]
    output_tokens = [token for chunk in chunks for token in _tokens(chunk)]
    reference_counter = Counter(reference_tokens)
    output_counter = Counter(output_tokens)
    lost = sum((reference_counter - output_counter).values())
    duplicated = sum((output_counter - reference_counter).values())
    matched = max(0, len(reference_tokens) - lost)
    coverage_ppm = round(matched * 1_000_000 / len(reference_tokens)) if reference_tokens else 0
    position_matches = sum(
        1 for left, right in zip(reference_tokens, output_tokens) if left == right
    )
    order_ppm = round(
        position_matches * 1_000_000 / max(1, len(reference_tokens), len(output_tokens))
    )
    candidate_boundaries = set(_boundary_positions(chunks))
    if boundary_kind in {"paragraph", "sentence", "page"}:
        expected = set(model["boundaries"][boundary_kind])
    elif boundary_kind == "heading":
        expected = set(_boundary_positions(_heading_chunks(model)))
    elif boundary_kind == "document":
        expected = set()
    else:
        expected = set()
    boundary_precision = (
        round(len(candidate_boundaries & expected) * 1_000_000 / len(candidate_boundaries))
        if candidate_boundaries
        else 1_000_000
    ) if boundary_kind is not None else None
    boundary_recall = (
        round(len(candidate_boundaries & expected) * 1_000_000 / len(expected))
        if expected
        else (1_000_000 if not candidate_boundaries else 0)
    ) if boundary_kind is not None else None
    contamination = 0
    # O texto de ruído foi removido antes da referência; este contador prova que
    # nenhum segmentador o reintroduziu durante a execução.
    if model["noise"] and output_tokens != reference_tokens:
        contamination = sum(entry["occurrences"] for entry in model["noise"])
    cross_total = len(model["cross_page"])
    cross_passed = cross_total
    diagnostics: list[str] = []
    if method == "page-layout" and cross_total:
        cross_passed = 0
        diagnostics.append("page-break-crosses-unit")
    if lost:
        diagnostics.append("token-loss")
    if duplicated:
        diagnostics.append("token-duplication")
    if order_ppm != 1_000_000:
        diagnostics.append("token-order")
    if contamination:
        diagnostics.append("noise-contamination")
    if boundary_precision is not None and boundary_precision != 1_000_000:
        diagnostics.append("boundary-mismatch")
    exact = not lost and not duplicated and order_ppm == 1_000_000 and not contamination
    if method == "page-layout" and cross_total:
        status = "rejected"
    elif not exact:
        status = "rejected"
    elif boundary_kind is not None and boundary_precision != 1_000_000:
        status = "rejected"
    else:
        status = "passed"
    duration_ms = max(1, round((time.perf_counter_ns() - started) / 1_000_000))
    throughput = round(len(model["text"]) * 1000 / max(1, duration_ms))
    token_error_ppm = min(
        1_000_000,
        round((lost + duplicated + contamination) * 1_000_000 / max(1, len(reference_tokens))),
    )
    boundary_error_ppm = (
        1_000_000 - boundary_precision
        if boundary_precision is not None
        else 0
    )
    continuity_error_ppm = (
        round((cross_total - cross_passed) * 1_000_000 / cross_total)
        if cross_total
        else 0
    )
    error_ppm = max(token_error_ppm, boundary_error_ppm, continuity_error_ppm)
    accuracy_ppm = min(coverage_ppm, order_ppm, 1_000_000 - error_ppm)
    word_counts = [len(re.findall(r"\b\w+\b", chunk, re.UNICODE)) for chunk in chunks]
    return {
        "method": method,
        "implementation": f"{ANALYZER_ID}@{ANALYZER_VERSION}",
        "status": status,
        "tested_parameters": parameters,
        "chunk_count": len(chunks),
        "_duration_ms": duration_ms,
        "_throughput_chars_per_second": throughput,
        "efficiency": {
            "characters_per_chunk": round(len(model["text"]) / max(1, len(chunks))),
            "tokens_per_chunk": round(len(reference_tokens) / max(1, len(chunks))),
            "boundary_checks": len(candidate_boundaries),
        },
        "chunk_words": {
            "minimum": min(word_counts) if word_counts else 0,
            "median": round(statistics.median(word_counts)) if word_counts else 0,
            "maximum": max(word_counts) if word_counts else 0,
        },
        "metrics": {
            "coverage_ppm": coverage_ppm,
            "order_ppm": order_ppm,
            "lost_tokens": lost,
            "duplicated_tokens": duplicated,
            "contamination_occurrences": contamination,
            "boundary_precision_ppm": boundary_precision,
            "boundary_recall_ppm": boundary_recall,
            "cross_page_total": cross_total,
            "cross_page_reconstructed": cross_passed,
            "accuracy_ppm": accuracy_ppm,
            "error_ppm": error_ppm,
        },
        "proof": {
            "reference_tokens_sha256": _token_hash(reference_tokens),
            "output_tokens_sha256": _token_hash(output_tokens),
            "boundaries_sha256": _fingerprint(sorted(candidate_boundaries)),
        },
        "diagnostics": diagnostics,
    }


def _run_experiments(report: dict, context: dict) -> list[dict]:
    model = report["_model"]
    if not model["complete"] or not model["tokens"]:
        return [
            {
                "method": "whole-document",
                "implementation": f"{ANALYZER_ID}@{ANALYZER_VERSION}",
                "status": "inconclusive",
                "tested_parameters": {"boundary": "document"},
                "chunk_count": 0,
                "_duration_ms": 0,
                "_throughput_chars_per_second": 0,
                "efficiency": {
                    "characters_per_chunk": 0,
                    "tokens_per_chunk": 0,
                    "boundary_checks": 0,
                },
                "chunk_words": {"minimum": 0, "median": 0, "maximum": 0},
                "metrics": {
                    "coverage_ppm": None,
                    "order_ppm": None,
                    "lost_tokens": 0,
                    "duplicated_tokens": 0,
                    "contamination_occurrences": 0,
                    "boundary_precision_ppm": None,
                    "boundary_recall_ppm": None,
                    "cross_page_total": 0,
                    "cross_page_reconstructed": 0,
                    "accuracy_ppm": None,
                    "error_ppm": None,
                },
                "proof": {
                    "reference_tokens_sha256": _token_hash(()),
                    "output_tokens_sha256": _token_hash(()),
                    "boundaries_sha256": _fingerprint([]),
                },
                "diagnostics": ["reference-unavailable"],
            }
        ]
    results = [
        _measure_experiment(method, chunks, parameters, boundary_kind, model)
        for method, chunks, parameters, boundary_kind in _candidate_runs(report, context)
    ]
    return sorted(
        results,
        key=lambda value: (
            value["status"] != "passed",
            -(value["metrics"]["accuracy_ppm"] or 0),
            -(value["metrics"]["boundary_recall_ppm"] or 0),
            value["efficiency"]["boundary_checks"],
            value["method"],
        ),
    )


def _publication_context(directory: Path) -> tuple[dict, Path | None]:
    metadata_paths = sorted(directory.glob("*.source.json"))
    if len(metadata_paths) != 1:
        return {}, None
    metadata_path = metadata_paths[0]
    try:
        document = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}, metadata_path
    identity = document.get("identity") if isinstance(document, dict) else None
    return (dict(identity) if isinstance(identity, dict) else {}), metadata_path


def _distribution(values: list[int]) -> dict | None:
    if not values:
        return None
    ordered = sorted(values)
    return {
        "minimum": ordered[0],
        "median": round(statistics.median(ordered)),
        "maximum": ordered[-1],
    }


def _magnitude_bucket(value: object) -> str:
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        return "unknown"
    for ceiling, label in (
        (0, "0"),
        (1, "1"),
        (9, "2-9"),
        (49, "10-49"),
        (199, "50-199"),
        (999, "200-999"),
    ):
        if number <= ceiling:
            return label
    return "1000+"


def _structural_profile(report: dict, context: dict) -> str:
    structure = report["structure"]
    return _fingerprint(
        {
            "format": report["format"],
            "parser": report["parser"]["selected"],
            "type": context.get("type"),
            "language": context.get("language"),
            "pages": _magnitude_bucket(structure.get("pages", structure.get("spine_documents"))),
            "paragraphs": _magnitude_bucket(structure.get("paragraphs")),
            "headings": _magnitude_bucket(structure.get("headings", structure.get("heading_candidates"))),
            "noise": bool(structure.get("noise_patterns")),
            "cross_page": bool(structure.get("cross_page_continuations")),
            "reversible": bool(structure.get("reversible_manifest")),
        }
    )


def rebuild_learning(source_root: Path, catalog_hash: str | None = None) -> Path:
    """Agrega resultados experimentais sem copiar texto ou explicações."""

    root = source_root.resolve()
    if catalog_hash is None:
        _document, catalog_hash = _catalog()
    groups: dict[str, dict] = {}
    manifests = 0
    for path in sorted(root.rglob("*.chunking.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(value, dict) or value.get("schema_version") != MANIFEST_SCHEMA:
            continue
        manifests += 1
        profile = str((value.get("knowledge") or {}).get("profile") or "")
        for experiment in value.get("experiments") or []:
            if not isinstance(experiment, dict):
                continue
            key_value = {
                "profile": profile,
                "method": experiment.get("method"),
                "implementation": experiment.get("implementation"),
                "parameters": experiment.get("tested_parameters"),
            }
            key = _fingerprint(key_value)
            group = groups.setdefault(
                key,
                {
                    "id": key,
                    **key_value,
                    "status_counts": Counter(),
                    "accuracy": [],
                    "error": [],
                    "characters_per_chunk": [],
                    "tokens_per_chunk": [],
                },
            )
            group["status_counts"][str(experiment.get("status") or "inconclusive")] += 1
            metrics = experiment.get("metrics") or {}
            for field, target in (
                ("accuracy_ppm", "accuracy"),
                ("error_ppm", "error"),
            ):
                if isinstance(metrics.get(field), int):
                    group[target].append(metrics[field])
            efficiency = experiment.get("efficiency") or {}
            for field in ("characters_per_chunk", "tokens_per_chunk"):
                if isinstance(efficiency.get(field), int):
                    group[field].append(efficiency[field])
    profiles = []
    for key in sorted(groups):
        group = groups[key]
        profiles.append(
            {
                "id": group["id"],
                "profile": group["profile"],
                "method": group["method"],
                "implementation": group["implementation"],
                "parameters": group["parameters"],
                "assets": sum(group["status_counts"].values()),
                "status_counts": dict(sorted(group["status_counts"].items())),
                "metrics": {
                    "accuracy_ppm": _distribution(group["accuracy"]),
                    "error_ppm": _distribution(group["error"]),
                    "characters_per_chunk": _distribution(group["characters_per_chunk"]),
                    "tokens_per_chunk": _distribution(group["tokens_per_chunk"]),
                },
            }
        )
    document = {
        "schema_version": LEARNING_SCHEMA,
        "generator": {"id": ANALYZER_ID, "version": ANALYZER_VERSION},
        "catalog": {"schema": CATALOG_SCHEMA, "sha256": catalog_hash},
        "manifests": manifests,
        "profiles": profiles,
        "integrity": _fingerprint(profiles),
    }
    target = learning_path_for(root)
    _write_json_if_changed(target, document)
    return target


def _analyze_assets(
    publication: Path,
    assets: list[Path],
    source_root: Path,
    reporter: PublicationReporter | None = None,
    rebuild_after: bool = True,
    reuse_existing: bool = False,
    force_recalculate: bool = False,
    now: datetime | None = None,
) -> list[Path]:
    """Executa e prova experimentos para o conjunto explicitamente solicitado."""

    root = source_root.resolve()
    if not publication.is_dir() or (publication != root and root not in publication.parents):
        raise AnalysisError("publicação fora da raiz configurada")
    if not assets:
        raise AnalysisError(f"publicação sem EPUB/PDF: {publication}")
    catalog, catalog_hash = _catalog()
    context, metadata_path = _publication_context(publication)
    current_time = _effective_now(now)
    written = []
    recalculated = False
    for asset in assets:
        target = manifest_path_for(asset)
        evidence = hash_file(asset)
        current = _current_manifest(target, evidence, catalog_hash, metadata_path)
        age = _successful_age(current, current_time) if current is not None else None
        fresh = age is not None and age < FRESHNESS_WINDOW
        if current is not None and not force_recalculate and fresh:
            if reporter is not None:
                reporter.notice(
                    "Análise reutilizada",
                    f"{asset.relative_to(root).as_posix()} · menos de 24 h",
                )
            written.append(target)
            continue
        report = inspect_asset(asset, evidence)
        experiments = _run_experiments(report, context)
        persisted_experiments = [
            {key: value for key, value in experiment.items() if not key.startswith("_")}
            for experiment in experiments
        ]
        model = report["_model"]
        validated = [
            entry
            for entry in experiments
            if entry["status"] == "passed"
            and entry["method"] not in {"fixed-window", "whole-document"}
            and entry["metrics"]["boundary_precision_ppm"] is not None
        ]
        profile = _structural_profile(report, context)
        document = {
            "schema_version": MANIFEST_SCHEMA,
            "generator": {"id": ANALYZER_ID, "version": ANALYZER_VERSION},
            "execution": {
                "status": "completed",
                "completed_at": current_time.isoformat().replace("+00:00", "Z"),
            },
            "catalog": {
                "id": catalog["catalog_id"],
                "schema": catalog["schema_version"],
                "version": catalog["version"],
                "path": CATALOG_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
                "sha256": catalog_hash,
            },
            "asset": {
                "path": asset.relative_to(root).as_posix(),
                "format": report["format"],
                "size": report["size"],
                "hashes": report["hashes"],
            },
            "publication": {
                "metadata": (
                    metadata_path.relative_to(root).as_posix()
                    if metadata_path is not None
                    else None
                ),
                "remote_id": context.get("remote_id"),
                "author_key": context.get("author_key"),
                "language": context.get("language"),
                "category": context.get("category"),
                "type": context.get("type"),
                "generated_epub": bool(
                    report["format"] == "epub"
                    and report["structure"].get("reversible_manifest")
                ),
            },
            "parser": report["parser"],
            "metadata_evidence": report["metadata_evidence"],
            "structure": report["structure"],
            "fingerprint": report["fingerprint"],
            "reference": {
                "complete": model["complete"],
                "characters": len(model["text"]),
                "tokens": len(model["tokens"]),
                "blocks": len(model["blocks"]),
                "paragraph_boundaries": len(model["boundaries"]["paragraph"]),
                "sentence_boundaries": len(model["boundaries"]["sentence"]),
                "page_boundaries": len(model["boundaries"]["page"]),
                "noise_patterns_removed": len(model["noise"]),
                "noise_occurrences_removed": sum(entry["occurrences"] for entry in model["noise"]),
                "cross_page_continuations": len(model["cross_page"]),
                "tokens_sha256": _token_hash(model["tokens"]),
                "noise_proof_sha256": _fingerprint(model["noise"]),
                "continuity_proof_sha256": _fingerprint(model["cross_page"]),
            },
            "experiments": persisted_experiments,
            "recommendation": {
                "status": "validated" if validated else "inconclusive",
                "method": validated[0]["method"] if validated else None,
                "experiment_proof": validated[0]["proof"] if validated else None,
            },
            "knowledge": {
                "schema": LEARNING_SCHEMA,
                "path": learning_path_for(root).relative_to(root).as_posix(),
                "profile": profile,
            },
            "limitations": report["limitations"],
            "chunks_materialized": False,
            "integrity": _fingerprint(
                {
                    "asset": report["hashes"],
                    "fingerprint": report["fingerprint"],
                    "catalog": catalog_hash,
                    "reference": _token_hash(model["tokens"]),
                    "experiments": persisted_experiments,
                    "analyzer_version": ANALYZER_VERSION,
                }
            ),
        }
        _write_json_if_changed(target, document)
        recalculated = True
        if reporter is not None:
            reporter.experiments(asset.relative_to(root), experiments)
        written.append(target)
    if rebuild_after and (recalculated or not learning_path_for(root).is_file()):
        rebuild_learning(root, catalog_hash)
    return written


def analyze_publication(
    directory: Path,
    source_root: Path,
    reporter: PublicationReporter | None = None,
    *,
    rebuild_after: bool = True,
    reuse_existing: bool = False,
    force_recalculate: bool = False,
    now: datetime | None = None,
) -> list[Path]:
    """Analisa todos os EPUB/PDF diretos de uma publicação como uma unidade."""

    publication = directory.resolve()
    assets = sorted(
        path
        for path in publication.iterdir()
        if path.is_file() and path.suffix.casefold() in {".epub", ".pdf"}
    ) if publication.is_dir() else []
    return _analyze_assets(
        publication,
        assets,
        source_root,
        reporter,
        rebuild_after=rebuild_after,
        reuse_existing=reuse_existing,
        force_recalculate=force_recalculate,
        now=now,
    )


def publication_directories(target: Path, source_root: Path) -> list[Path]:
    """Resolve arquivo, publicação ou subárvore para diretórios canônicos."""

    root = source_root.resolve()
    candidate = target.resolve()
    if candidate != root and root not in candidate.parents:
        raise AnalysisError("escopo fora da raiz de publicações")
    if candidate.is_file():
        raise AnalysisError("arquivo deve ser tratado como ativo específico")
    if not candidate.is_dir():
        raise AnalysisError("escopo de análise inexistente")
    direct_assets = list(candidate.glob("*.epub")) + list(candidate.glob("*.pdf"))
    if direct_assets:
        return [candidate]
    directories = {
        path.parent
        for pattern in ("*.epub", "*.pdf")
        for path in candidate.rglob(pattern)
        if path.is_file()
    }
    return sorted(directories)


def analyze_scope(
    target: Path,
    source_root: Path,
    reporter: PublicationReporter | None = None,
    *,
    reuse_existing: bool = False,
    force_recalculate: bool = False,
    now: datetime | None = None,
) -> list[Path]:
    candidate = target.resolve()
    root = source_root.resolve()
    if candidate.is_file():
        if candidate != root and root not in candidate.parents:
            raise AnalysisError("ativo fora da raiz de publicações")
        if candidate.suffix.casefold() not in {".epub", ".pdf"}:
            raise AnalysisError("--asset exige EPUB ou PDF")
        return _analyze_assets(
            candidate.parent,
            [candidate],
            root,
            reporter,
            reuse_existing=reuse_existing,
            force_recalculate=force_recalculate,
            now=now,
        )
    written = []
    for directory in publication_directories(target, source_root):
        written.extend(
            analyze_publication(
                directory,
                source_root,
                reporter,
                rebuild_after=False,
                reuse_existing=reuse_existing,
                force_recalculate=force_recalculate,
                now=now,
            )
        )
    if not written:
        raise AnalysisError("escopo sem ativos analisáveis")
    _catalog_document, catalog_hash = _catalog()
    rebuild_learning(root, catalog_hash)
    return written


def analyze_and_commit_scope(
    target: Path,
    source_root: Path,
    config: dict,
    reporter: PublicationReporter | None = None,
    *,
    force_recalculate: bool = False,
    reset: bool = False,
) -> tuple[list[Path], list[str]]:
    """Fecha e commita cada publicação do escopo pela transação compartilhada."""

    from publication_index import configured_index_path, update_global_index
    from publication_transaction import (
        GlobalProgressJournal,
        GitPublicationPublisher,
        catalog_item_from_publication,
        progress_fingerprint,
    )

    root = source_root.resolve()
    candidate = target.resolve()
    asset = candidate if candidate.is_file() else None
    if asset is not None and asset.suffix.casefold() not in {".epub", ".pdf"}:
        raise AnalysisError("--asset exige EPUB ou PDF")
    directories = [candidate.parent] if asset is not None else publication_directories(candidate, root)
    if not directories:
        raise AnalysisError("escopo sem ativos analisáveis")
    by_identity = {
        directory.relative_to(root).as_posix(): directory for directory in directories
    }
    order = list(by_identity)
    paths = runtime_paths(config, REPOSITORY_ROOT)
    index_path = configured_index_path(config)
    publisher = GitPublicationPublisher(
        REPOSITORY_ROOT,
        root,
        paths["locks"] / "publication-git.lock",
        branch=str(config["transaction"]["branch"]),
        index_path=index_path,
    )
    ledger = AcquisitionLedger(paths["acquisition"] / "ledger.json")
    global_mode = candidate == root
    journal = (
        GlobalProgressJournal(
            paths["logs"] / "publication-analysis.global.json",
            tool="publication_analysis.py",
            scope="all",
            fingerprint=progress_fingerprint(
                {
                    "analyzer": ANALYZER_VERSION,
                    "catalog": _catalog()[1],
                    "source_root": str(config["source_root"]),
                }
            ),
            order=order,
            reset=reset,
        )
        if global_mode
        else None
    )
    if journal is not None:
        order = journal.order
        directories = [by_identity[identity] for identity in order]
    written: list[Path] = []
    commits: list[str] = []
    for position, directory in enumerate(directories):
        identity = order[position]
        if journal is not None and position < journal.next_index:
            if reporter is not None:
                reporter.notice("Publicação retomada", identity)
            continue
        item = catalog_item_from_publication(directory)
        previous = ledger.get(item.stable_key()) or {}
        publisher.preflight(
            item,
            resume=previous.get("git_state") == "commit_pending",
        )
        if journal is not None:
            journal.record(position, identity, "analysis")

        def operation() -> tuple[list[Path], Path]:
            manifests = (
                _analyze_assets(
                    directory,
                    [asset],
                    root,
                    reporter,
                    force_recalculate=force_recalculate,
                )
                if asset is not None
                else analyze_publication(
                    directory,
                    root,
                    reporter,
                    force_recalculate=force_recalculate,
                )
            )
            updated = update_global_index(
                root,
                index_path,
                config,
                publication=directory,
            )
            return manifests, updated

        (manifests, _updated), commit = publisher.finalize(item, ledger, operation)
        written.extend(manifests)
        if commit:
            commits.append(commit)
        if journal is not None:
            journal.confirm(position, identity, commit=commit)
    return written, commits


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analisa estruturas EPUB/PDF e recomenda chunking sem gerar chunks."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="mantido por compatibilidade; o reuso válido por 24 h já é automático",
    )
    parser.add_argument(
        "--force-recalculate",
        action="store_true",
        help="ignora a conclusão válida das últimas 24 horas e recalcula",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="descarta somente o diário global do analisador antes de --all",
    )
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--asset", type=Path)
    scope.add_argument("--publication", type=Path)
    scope.add_argument("--scope", type=Path)
    scope.add_argument("--all", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    reporter: PublicationReporter | None = None
    try:
        arguments = _parser().parse_args(list(argv) if argv is not None else None)
        reporter = PublicationReporter(
            "Laboratório experimental",
            compact=bool(arguments.all or arguments.scope),
        )
        config = load_config(arguments.config)
        source_root = resolve_repository_path(config["source_root"], REPOSITORY_ROOT)
        target = source_root if arguments.all else (
            arguments.asset or arguments.publication or arguments.scope
        )
        reporter.start(str(target))
        if arguments.reset and not arguments.all:
            raise AnalysisError("--reset exige --all")
        paths, commits = analyze_and_commit_scope(
            Path(target),
            source_root,
            config,
            reporter,
            force_recalculate=arguments.force_recalculate,
            reset=arguments.reset,
        )
        reporter.result(
            "Análise concluída",
            {
                "manifestos": len(paths),
                "aprendizado": learning_path_for(source_root),
                "commits": len(commits),
            },
        )
        return 0
    except (AnalysisError, ContractError, OSError) as error:
        (reporter or PublicationReporter("Laboratório experimental")).error("Análise", error)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
