# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Analisa EPUB/PDF e recomenda estratégias de chunking sem criar chunks.

A capacidade é deliberadamente local e determinística. Ela inspeciona a
estrutura do ativo, correlaciona fingerprints já conhecidos no corpus e grava
um manifesto derivado ao lado do arquivo analisado. Nenhum texto editorial é
persistido no manifesto.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
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
    validate_file_signature,
    write_json_atomic,
)


MANIFEST_SCHEMA = "publication-chunking-analysis/v1"
ANALYZER_ID = "egwSearch/publication_analysis.py"
ANALYZER_VERSION = "1"
MAX_ZIP_ENTRIES = 10_000
MAX_ZIP_EXPANDED = 512 * 1024 * 1024
MAX_XML_BYTES = 16 * 1024 * 1024
MAX_EPUB_TEXT_BYTES = 128 * 1024 * 1024
MAX_PDF_SAMPLE_PAGES = 32


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


def _safe_zip_entries(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    infos = archive.infolist()
    if not infos or len(infos) > MAX_ZIP_ENTRIES:
        raise AnalysisError("EPUB excede cardinalidade segura de entradas")
    expanded = 0
    for info in infos:
        name = info.filename
        path = PurePosixPath(name)
        if (
            not name
            or "\\" in name
            or path.is_absolute()
            or ".." in path.parts
            or len(name) > 512
        ):
            raise AnalysisError("EPUB contém path interno inseguro")
        expanded += info.file_size
        if expanded > MAX_ZIP_EXPANDED:
            raise AnalysisError("EPUB excede tamanho expandido seguro")
        if info.compress_size and info.file_size / info.compress_size > 200:
            raise AnalysisError("EPUB excede razão segura de expansão")
    return infos


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
        total_text_bytes = 0
        for content_path in content_paths:
            root = _xml(archive, content_path)
            text = " ".join("".join(root.itertext()).split())
            total_text_bytes += len(text.encode("utf-8"))
            if total_text_bytes > MAX_EPUB_TEXT_BYTES:
                raise AnalysisError("EPUB excede limite de texto analisável")
            counts["words"] += len(re.findall(r"\b\w+\b", text, re.UNICODE))
            counts["sentences"] += _sentence_count(text)
            for element in root.iter():
                local = _local_name(element.tag)
                if local in {"p", "li", "blockquote", "td"}:
                    if " ".join("".join(element.itertext()).split()):
                        counts["paragraphs"] += 1
                if re.fullmatch(r"h[1-6]", local):
                    value = " ".join("".join(element.itertext()).split())
                    if value:
                        counts["headings"] += 1
                        heading_levels[local] += 1
                        if len(title_samples) < 128:
                            title_samples.append(value)
                if local in {"section", "article"}:
                    counts[local] += 1
                epub_type = _attribute_local(element, "type").casefold()
                if "pagebreak" in epub_type or _attribute_local(element, "role") == "doc-pagebreak":
                    counts["pagebreaks"] += 1
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
        return {
            "parser": {
                "selected": "python-stdlib/zipfile+xml.etree",
                "candidates": [
                    {
                        "id": "python-stdlib/zipfile+xml.etree",
                        "status": "selected",
                        "reason": "OCF, pacote, spine e XHTML validados sem extração persistente",
                    },
                    {
                        "id": "ebooklib",
                        "status": "alternative",
                        "reason": "útil para interoperabilidade, dispensável para a inspeção estrutural atual",
                    },
                ],
                "confidence": 100,
            },
            "metadata_evidence": metadata,
            "structure": {
                **dict(sorted(counts.items())),
                "heading_levels": dict(sorted(heading_levels.items())),
            },
            "limitations": [],
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
            samples = _distributed_indices(pages, MAX_PDF_SAMPLE_PAGES)
            words = sentences = paragraphs = heading_candidates = 0
            for index in samples:
                page = document[index]
                try:
                    textpage = page.get_textpage()
                    try:
                        text = textpage.get_text_range()
                    finally:
                        textpage.close()
                finally:
                    page.close()
                normalized = "\n".join(line.rstrip() for line in text.splitlines())
                words += len(re.findall(r"\b\w+\b", normalized, re.UNICODE))
                sentences += _sentence_count(" ".join(normalized.split()))
                blocks = [part for part in re.split(r"\n\s*\n", normalized) if part.strip()]
                paragraphs += len(blocks)
                heading_candidates += sum(
                    1
                    for line in normalized.splitlines()
                    if 2 <= len(line.strip()) <= 120
                    and len(line.split()) <= 16
                    and (
                        line.strip().isupper()
                        or re.match(r"^(?:chapter|cap[ií]tulo|day|dia|article|artigo)\b", line.strip(), re.I)
                    )
                )
        finally:
            document.close()
        sample_ratio = len(samples) / pages if pages else 0
        structure = {
            "pages": pages,
            "sampled_pages": len(samples),
            "sample_ratio_ppm": round(sample_ratio * 1_000_000),
            "sample_words": words,
            "sample_sentences": sentences,
            "sample_paragraphs": paragraphs,
            "sample_heading_candidates": heading_candidates,
        }
        return {
            "parser": {
                "selected": "pypdfium2",
                "candidates": [
                    {
                        "id": "pypdfium2",
                        "status": "selected",
                        "reason": "parser mantido com paginação e camada textual sem regravação",
                    },
                    {
                        "id": "binary-pdf-structure",
                        "status": "fallback",
                        "reason": "somente contagem aproximada quando o parser principal falha",
                    },
                ],
                "confidence": 95 if words else 70,
            },
            "metadata_evidence": metadata,
            "structure": structure,
            "limitations": limitations + ([] if words else ["camada textual ausente ou vazia"]),
        }
    except Exception as error:
        payload = asset.read_bytes()
        pages = len(re.findall(rb"/Type\s*/Page\b", payload))
        return {
            "parser": {
                "selected": "binary-pdf-structure",
                "candidates": [
                    {
                        "id": "pypdfium2",
                        "status": "failed",
                        "reason": type(error).__name__,
                    },
                    {
                        "id": "binary-pdf-structure",
                        "status": "selected-fallback",
                        "reason": "inspeção limitada sem modificar o original",
                    },
                ],
                "confidence": 30,
            },
            "metadata_evidence": {},
            "structure": {"pages_approximate": pages},
            "limitations": ["texto e hierarquia não disponíveis no fallback binário"],
        }


def inspect_asset(asset: Path) -> dict:
    """Inspeciona o ativo uma vez e retorna somente sinais estruturais."""

    suffix = asset.suffix.casefold()
    if suffix == ".epub":
        publication_format = "epub"
        report = _epub_report(asset)
    elif suffix == ".pdf":
        publication_format = "pdf"
        report = _pdf_report(asset)
    else:
        raise AnalysisError(f"formato não analisável: {asset.name}")
    evidence = hash_file(asset)
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


def _score_strategies(report: dict, context: dict) -> list[dict]:
    structure = report["structure"]
    publication_type = str(context.get("type") or "").casefold()
    paragraphs = int(structure.get("paragraphs", structure.get("sample_paragraphs", 0)))
    sentences = int(structure.get("sentences", structure.get("sample_sentences", 0)))
    headings = int(structure.get("headings", structure.get("sample_heading_candidates", 0)))
    pages = int(structure.get("pages", structure.get("pages_approximate", 0)))
    articles = int(structure.get("article", 0))
    date_headings = int(structure.get("date_like_headings", 0))
    words = int(structure.get("words", structure.get("sample_words", 0)))
    is_devotional = publication_type in {"devocionais", "devotionals"}
    is_periodical = publication_type in {"periodicos", "periodicals"}

    definitions = [
        (
            "hierarchical-topic",
            "tópico hierárquico",
            min(100, 35 + headings * 4 + int(bool(structure.get("nav_documents"))) * 15),
            ["headings", "spine", "nav"],
            {"max_words": 1200, "preserve_subtree": True},
            "preserva capítulos, seções e microtópicos",
            "seções muito longas podem exigir subdivisão secundária",
        ),
        (
            "paragraph",
            "parágrafo",
            min(95, 30 + min(paragraphs, 65)),
            ["paragraphs"],
            {"max_words": 450, "merge_short": True},
            "fronteira editorial explícita e fácil reversão",
            "parágrafos curtos podem perder contexto sem fusão",
        ),
        (
            "sentence-window",
            "sentença com janela",
            min(90, 25 + min(sentences // 4, 65)),
            ["sentences"],
            {"sentences": 8, "overlap": 2},
            "granularidade fina para comparação experimental",
            "pode romper listas, citações e unidade retórica",
        ),
        (
            "page",
            "página",
            min(95, 25 + min(pages * 2, 70)),
            ["pages", "pagebreaks"],
            {"preserve_page": True},
            "localização bibliográfica direta quando paginação é autoritativa",
            "quebras de página nem sempre coincidem com semântica",
        ),
        (
            "devotional-day",
            "dia de meditação",
            min(100, 20 + (55 if is_devotional else 0) + min(date_headings * 8, 25)),
            ["publication_type", "date_like_headings"],
            {"one_day_per_chunk": True, "subdivide_by_heading": True},
            "preserva a unidade diária e sua data",
            "inadequada sem calendário ou cabeçalho diário comprovado",
        ),
        (
            "periodical-article",
            "artigo ou seção de periódico",
            min(100, 20 + (55 if is_periodical else 0) + min((articles + headings) * 3, 25)),
            ["publication_type", "article", "headings"],
            {"article_boundary": True, "subdivide_by_subheading": True},
            "mantém autoria e seção da edição",
            "artigos extensos podem exigir estratégia hierárquica composta",
        ),
        (
            "whole-document",
            "documento inteiro",
            80 if words and words <= 1800 else 20,
            ["words"],
            {"max_words": 1800},
            "baseline útil para documentos muito curtos",
            "custo e perda de precisão crescem rapidamente em obras longas",
        ),
    ]
    strategies = []
    for identifier, granularity, score, signals, parameters, benefit, risk in definitions:
        strategies.append(
            {
                "id": identifier,
                "granularity": granularity,
                "score": max(0, min(100, int(score))),
                "status": "candidate" if score >= 50 else "low-evidence",
                "signals": signals,
                "benefit": benefit,
                "risk": risk,
                "suggested_parameters": parameters,
                "materialize_chunks": False,
            }
        )
    return sorted(strategies, key=lambda value: (-value["score"], value["id"]))


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


def _read_corpus_profiles(source_root: Path, excluded: set[Path]) -> list[dict]:
    profiles = []
    for path in sorted(source_root.rglob("*.chunking.json")):
        if path.resolve() in excluded:
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            isinstance(value, dict)
            and value.get("schema_version") == MANIFEST_SCHEMA
            and isinstance(value.get("fingerprint"), str)
            and isinstance(value.get("publication"), dict)
        ):
            profiles.append(
                {
                    "fingerprint": value["fingerprint"],
                    "format": (value.get("asset") or {}).get("format"),
                    "type": value["publication"].get("type"),
                    "language": value["publication"].get("language"),
                    "category": value["publication"].get("category"),
                }
            )
    return profiles


def _correlation(report: dict, context: dict, profiles: list[dict]) -> dict:
    matching_fingerprint = sum(
        1 for profile in profiles if profile.get("fingerprint") == report["fingerprint"]
    )
    matching_type = sum(
        1
        for profile in profiles
        if context.get("type") and profile.get("type") == context.get("type")
    )
    matching_locale = sum(
        1
        for profile in profiles
        if context.get("language") and profile.get("language") == context.get("language")
    )
    matching_category = sum(
        1
        for profile in profiles
        if context.get("category") and profile.get("category") == context.get("category")
    )
    return {
        "corpus_manifests": len(profiles),
        "same_fingerprint": matching_fingerprint,
        "same_publication_type": matching_type,
        "same_language": matching_locale,
        "same_category": matching_category,
        "basis": "manifestos estruturais válidos; nenhum conteúdo textual compartilhado",
    }


def _analyze_assets(
    publication: Path,
    assets: list[Path],
    source_root: Path,
) -> list[Path]:
    """Produz manifestos coerentes para o conjunto explicitamente solicitado."""

    root = source_root.resolve()
    if not publication.is_dir() or (publication != root and root not in publication.parents):
        raise AnalysisError("publicação fora da raiz configurada")
    if not assets:
        raise AnalysisError(f"publicação sem EPUB/PDF: {publication}")
    context, metadata_path = _publication_context(publication)
    reports = [(asset, inspect_asset(asset)) for asset in assets]
    targets = {manifest_path_for(asset).resolve() for asset in assets}
    profiles = _read_corpus_profiles(root, targets)
    profiles.extend(
        {
            "fingerprint": report["fingerprint"],
            "format": report["format"],
            "type": context.get("type"),
            "language": context.get("language"),
            "category": context.get("category"),
        }
        for _asset, report in reports
    )
    written = []
    for asset, report in reports:
        strategies = _score_strategies(report, context)
        document = {
            "schema_version": MANIFEST_SCHEMA,
            "generator": {"id": ANALYZER_ID, "version": ANALYZER_VERSION},
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
            "correlation": _correlation(report, context, profiles),
            "recommended_strategy": strategies[0]["id"],
            "strategies": strategies,
            "limitations": report["limitations"],
            "chunks_materialized": False,
            "integrity": _fingerprint(
                {
                    "asset": report["hashes"],
                    "fingerprint": report["fingerprint"],
                    "strategies": strategies,
                    "analyzer_version": ANALYZER_VERSION,
                }
            ),
        }
        target = manifest_path_for(asset)
        _write_json_if_changed(target, document)
        written.append(target)
    return written


def analyze_publication(directory: Path, source_root: Path) -> list[Path]:
    """Analisa todos os EPUB/PDF diretos de uma publicação como uma unidade."""

    publication = directory.resolve()
    assets = sorted(
        path
        for path in publication.iterdir()
        if path.is_file() and path.suffix.casefold() in {".epub", ".pdf"}
    ) if publication.is_dir() else []
    return _analyze_assets(publication, assets, source_root)


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


def analyze_scope(target: Path, source_root: Path) -> list[Path]:
    candidate = target.resolve()
    root = source_root.resolve()
    if candidate.is_file():
        if candidate != root and root not in candidate.parents:
            raise AnalysisError("ativo fora da raiz de publicações")
        if candidate.suffix.casefold() not in {".epub", ".pdf"}:
            raise AnalysisError("--asset exige EPUB ou PDF")
        return _analyze_assets(candidate.parent, [candidate], root)
    written = []
    for directory in publication_directories(target, source_root):
        written.extend(analyze_publication(directory, source_root))
    if not written:
        raise AnalysisError("escopo sem ativos analisáveis")
    return written


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analisa estruturas EPUB/PDF e recomenda chunking sem gerar chunks."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--asset", type=Path)
    scope.add_argument("--publication", type=Path)
    scope.add_argument("--scope", type=Path)
    scope.add_argument("--all", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    try:
        arguments = _parser().parse_args(list(argv) if argv is not None else None)
        config = load_config(arguments.config)
        source_root = resolve_repository_path(config["source_root"], REPOSITORY_ROOT)
        target = source_root if arguments.all else (
            arguments.asset or arguments.publication or arguments.scope
        )
        paths = analyze_scope(Path(target), source_root)
        print(f"CHUNKING_ANALYSIS_OK manifests={len(paths)}")
        return 0
    except (AnalysisError, ContractError, OSError) as error:
        print(f"ERRO_ANALISE: {error}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
