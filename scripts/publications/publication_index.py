# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Gera e atualiza o índice global multilocalizado das publicações.

O gerador usa metadados locais como autoridade prioritária, calcula hashes dos
arquivos efetivamente publicados e mantém dados formativos separados de ativos
localmente derivados. A mesma API atende CLI, downloader e transação Git.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import threading
from typing import Iterable
from urllib.parse import quote, urlsplit

from publication_console import PublicationReporter

from publication_analysis import (
    MANIFEST_SCHEMA,
    analyze_and_commit_scope,
    extract_metadata_evidence,
    manifest_path_for,
)
from publication_contract import (
    ContractError,
    DEFAULT_CONFIG_PATH,
    REPOSITORY_ROOT,
    hash_file,
    load_config,
    read_source_records,
    resolve_repository_path,
    validate_file_signature,
    write_json_atomic,
)


INDEX_SCHEMA = "publication-global-index/v1"
INDEX_MANIFEST_SCHEMA = "publication-index-manifest/v1"
GENERATOR_ID = "egwSearch/publication_index.py"
GENERATOR_VERSION = "1"
_INDEX_LOCK = threading.Lock()

INDEX_MANIFEST = {
    "schema_version": INDEX_MANIFEST_SCHEMA,
    "describes": INDEX_SCHEMA,
    "notation": {"T?": "T|null", "T[]": "array<T>"},
    "root": {
        "schema_version": f"literal:{INDEX_SCHEMA}",
        "generation": "generation",
        "locales": "locale[]",
        "publications": "publication[]",
    },
    "types": {
        "generation": {
            "generator": "string",
            "version": "string",
            "configuration_sha256": "hex(64)",
            "source_fingerprint": "hex(64)",
        },
        "locale": {
            "language_path": "string",
            "category": "string",
            "type": "string",
            "publications": "integer",
        },
        "publication": {
            "id": "string",
            "remote_id": "string?",
            "title": "title",
            "author": "author",
            "localization": "localization",
            "tags": "string[]",
            "public_url": "string?",
            "path": "string",
            "metadata": "metadata",
            "cover": "resource?",
            "assets": "asset[]",
            "formative_state": "string",
            "formative_data": "formative?",
        },
        "title": {
            "original": "string",
            "normalized": "string",
            "route_slug": "string",
            "acronym": "string",
        },
        "author": {"name": "string", "key": "string"},
        "localization": {
            "language": "string",
            "language_path": "string",
            "category": "string",
            "type": "string",
        },
        "metadata": {"path": "string", "quality": "string"},
        "resource": {
            "path": "string",
            "url": "string",
            "size": "integer",
            "hashes": "hashes",
        },
        "asset": {
            "format": "pdf|epub",
            "path": "string",
            "url": "string",
            "size": "integer",
            "hashes": "hashes",
            "chunking_manifest": "string?",
        },
        "hashes": {"sha1": "hex(40)", "sha256": "hex(64)", "sha512": "hex(128)"},
        "formative": {"book": "book", "urls": "url[]", "global_hashes": "global_hash[]"},
        "book": {
            "title": "string",
            "contributors": "contributor[]",
            "edition": "object",
            "language": "string",
            "primary_category": "string",
            "tags": "string[]",
        },
        "contributor": {"name": "string", "role": "string"},
        "url": {"format": "pdf|epub", "url": "string"},
        "global_hash": {
            "format": "pdf|epub",
            "sha1": "hex(40)",
            "sha256": "hex(64)",
            "sha512": "hex(128)",
        },
    },
}


class IndexError(ContractError):
    """Representa metadado ou cobertura incompatível com o índice global."""


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


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise IndexError(f"JSON inválido: {path}") from error


def _metadata_paths(source_root: Path, scope: Path | None = None) -> list[Path]:
    root = source_root.resolve()
    target = (scope or root).resolve()
    if target != root and root not in target.parents:
        raise IndexError("escopo do índice fora da raiz configurada")
    if target.is_file():
        if not target.name.endswith(".source.json"):
            target = target.parent
        else:
            return [target]
    if not target.is_dir():
        raise IndexError("escopo do índice inexistente")
    direct = sorted(target.glob("*.source.json"))
    if direct:
        if len(direct) != 1:
            raise IndexError(f"publicação com metadados ambíguos: {target}")
        return direct
    return sorted(target.rglob("*.source.json"))


def _route_parts(directory: Path, source_root: Path) -> dict:
    parts = directory.relative_to(source_root).parts
    if len(parts) == 4:
        author_key, language_path, publication_type, route_slug = parts
        category = author_key
    elif len(parts) == 5:
        category, author_key, language_path, publication_type, route_slug = parts
    else:
        raise IndexError(f"path de publicação não canônico: {directory}")
    return {
        "category": category,
        "author_key": author_key,
        "language_path": language_path,
        "type": publication_type,
        "route_slug": route_slug,
    }


def _remote_id(records: list[dict]) -> str:
    for record in records:
        url = str(record.get("url") or "")
        match = re.search(r"/(?:book/b|read/)(\d+)(?:[./]|$)", urlsplit(url).path)
        if match:
            return match.group(1)
    return ""


def _legacy_identity(
    metadata_path: Path,
    records: list[dict],
    source_root: Path,
    config: dict,
) -> dict:
    route = _route_parts(metadata_path.parent, source_root)
    evidence = {}
    candidates = sorted(metadata_path.parent.glob("*.epub"))
    candidates.extend(sorted(metadata_path.parent.glob("*.pdf")))
    for candidate in candidates:
        try:
            candidate_evidence = extract_metadata_evidence(candidate)
        except (ContractError, OSError):
            continue
        if candidate_evidence.get("title"):
            evidence = candidate_evidence
            break
    title = str(evidence.get("title") or "").strip()
    if not title:
        raise IndexError(
            f"metadado legado sem título editorial extraível: {metadata_path}"
        )
    author_name = str(evidence.get("creator") or "").strip()
    configured = (config.get("authors") or {}).get(route["author_key"], {})
    if not author_name:
        author_name = str(configured.get("name") or "").strip()
    if not author_name:
        raise IndexError(
            f"metadado legado sem autoria editorial extraível: {metadata_path}"
        )
    language = str(evidence.get("language") or route["language_path"]).strip()
    return {
        "remote_id": _remote_id(records),
        "author_original": author_name,
        "author_key": route["author_key"],
        "title_original": title,
        "title_normalized": title,
        "language_original": language,
        "language": "pt-BR" if route["language_path"] == "pt-br" else "en",
        "language_path": route["language_path"],
        "category_original": route["category"],
        "category": route["category"],
        "type": route["type"],
        "edition": "",
        "acronym": metadata_path.name.removesuffix(".source.json"),
        "route_slug": route["route_slug"],
        "tags": [],
        "public_url": next(
            (
                str(record.get("url"))
                for record in records
                if re.search(r"/(?:book/b|read/)\d+", str(record.get("url") or ""))
            ),
            "",
        ),
    }


def _asset_record(asset: Path, source_root: Path, public_root: str) -> dict:
    publication_format = asset.suffix.casefold().lstrip(".")
    validate_file_signature(asset, publication_format)
    hashes = hash_file(asset)
    manifest_path = manifest_path_for(asset)
    manifest_relative = None
    if manifest_path.is_file():
        manifest = _read_json(manifest_path)
        if (
            not isinstance(manifest, dict)
            or manifest.get("schema_version") != MANIFEST_SCHEMA
            or (manifest.get("asset") or {}).get("hashes", {}).get("sha512")
            != hashes.sha512
        ):
            raise IndexError(f"manifesto de análise divergente: {manifest_path}")
        manifest_relative = manifest_path.relative_to(source_root).as_posix()
    relative = asset.relative_to(source_root).as_posix()
    encoded = "/".join(quote(part, safe="-._~") for part in relative.split("/"))
    return {
        "format": publication_format,
        "path": relative,
        "url": f"{public_root.rstrip('/')}/{encoded}",
        "size": hashes.size,
        "hashes": hashes.as_dict(),
        "chunking_manifest": manifest_relative,
    }


def _cover_record(directory: Path, source_root: Path, public_root: str) -> dict | None:
    cover = directory / "cover.png"
    if not cover.is_file():
        return None
    hashes = hash_file(cover)
    relative = cover.relative_to(source_root).as_posix()
    encoded = "/".join(quote(part, safe="-._~") for part in relative.split("/"))
    return {
        "path": relative,
        "url": f"{public_root.rstrip('/')}/{encoded}",
        "size": hashes.size,
        "hashes": hashes.as_dict(),
    }


def _full_original(record: dict) -> bool:
    hashes = record.get("hashes") or {}
    return (
        record.get("format") in {"pdf", "epub"}
        and isinstance(record.get("url"), str)
        and urlsplit(record["url"]).scheme in {"http", "https"}
        and re.fullmatch(r"[0-9a-f]{40}", str(hashes.get("sha1") or "")) is not None
        and re.fullmatch(r"[0-9a-f]{64}", str(hashes.get("sha256") or "")) is not None
        and re.fullmatch(r"[0-9a-f]{128}", str(hashes.get("sha512") or "")) is not None
    )


def _formative(identity: dict, records: list[dict]) -> tuple[str, dict | None]:
    originals = [record for record in records if _full_original(record)]
    formats = {record["format"] for record in originals}
    if not originals:
        return "not-applicable-local-derivation", None
    if len(formats) != len(originals):
        # Múltiplas URLs para os mesmos bytes são permitidas somente quando a
        # matriz é idêntica; hashes permanecem um item por formato.
        matrices = {
            (record["format"], json.dumps(record["hashes"], sort_keys=True))
            for record in originals
        }
        if len(matrices) != len(formats):
            return "conflicting-original-evidence", None
    order = {"pdf": 0, "epub": 1}
    urls = [
        {"format": record["format"], "url": record["url"]}
        for record in sorted(originals, key=lambda value: (order[value["format"]], value["url"]))
    ]
    hashes_by_format = {}
    for record in originals:
        hashes_by_format[record["format"]] = {
            "format": record["format"],
            "sha1": record["hashes"]["sha1"],
            "sha256": record["hashes"]["sha256"],
            "sha512": record["hashes"]["sha512"],
        }
    document = {
        "book": {
            "title": identity["title_normalized"],
            "contributors": [
                {"name": identity["author_original"], "role": "author"}
            ],
            "edition": {},
            "language": (
                "pt-br" if identity["language_path"] == "pt-br" else "en"
            ),
            "primary_category": identity["type"],
            "tags": sorted(set(identity.get("tags") or [])),
        },
        "urls": urls,
        "global_hashes": [
            hashes_by_format[value]
            for value in ("pdf", "epub")
            if value in hashes_by_format
        ],
    }
    return "available", document


def build_index_entry(metadata_path: Path, source_root: Path, config: dict) -> dict:
    """Materializa uma entrada validada a partir de metadado e bytes locais."""

    value = _read_json(metadata_path)
    if not isinstance(value, dict):
        raise IndexError(f"metadado deve ser objeto: {metadata_path}")
    records = read_source_records(metadata_path)
    if value.get("schema_version") == "publication-source/v3":
        if value.get("state") != "completed":
            raise IndexError(f"publicação ainda não concluída: {metadata_path}")
        identity = dict(value.get("identity") or {})
        records = list(value.get("sources") or [])
        metadata_quality = "canonical-v3"
    else:
        identity = _legacy_identity(metadata_path, records, source_root, config)
        metadata_quality = "legacy-editorial-extraction"

    required = {
        "author_original",
        "author_key",
        "title_original",
        "title_normalized",
        "language",
        "language_path",
        "category",
        "type",
        "acronym",
        "route_slug",
    }
    if any(not isinstance(identity.get(key), str) or not identity[key] for key in required):
        raise IndexError(f"identidade incompleta: {metadata_path}")
    public_root = str(config.get("public_root") or "/publications")
    assets = [
        _asset_record(asset, source_root, public_root)
        for asset in sorted(metadata_path.parent.iterdir())
        if asset.is_file() and asset.suffix.casefold() in {".pdf", ".epub"}
    ]
    if not assets:
        raise IndexError(f"publicação sem ativo editorial: {metadata_path}")
    formative_state, formative_data = _formative(identity, records)
    relative_directory = metadata_path.parent.relative_to(source_root).as_posix()
    remote_id = str(identity.get("remote_id") or _remote_id(records))
    stable_suffix = remote_id or _fingerprint(relative_directory)[:16]
    item = {
        "id": (
            f"{identity['author_key']}:{identity['language_path']}:"
            f"{identity['category']}:{identity['type']}:{stable_suffix}"
        ),
        "remote_id": remote_id or None,
        "title": {
            "original": identity["title_original"],
            "normalized": identity["title_normalized"],
            "route_slug": identity["route_slug"],
            "acronym": identity["acronym"],
        },
        "author": {
            "name": identity["author_original"],
            "key": identity["author_key"],
        },
        "localization": {
            "language": identity["language"],
            "language_path": identity["language_path"],
            "category": identity["category"],
            "type": identity["type"],
        },
        "tags": sorted(set(identity.get("tags") or [])),
        "public_url": identity.get("public_url") or None,
        "path": relative_directory,
        "metadata": {
            "path": metadata_path.relative_to(source_root).as_posix(),
            "quality": metadata_quality,
        },
        "cover": _cover_record(metadata_path.parent, source_root, public_root),
        "assets": sorted(assets, key=lambda asset: (asset["format"] != "pdf", asset["path"])),
        "formative_state": formative_state,
        "formative_data": formative_data,
    }
    return item


def _sort_key(item: dict) -> tuple:
    return (
        item["title"]["normalized"].casefold(),
        item["author"]["key"],
        item["localization"]["language_path"],
        item["localization"]["category"],
        item["localization"]["type"],
        item["id"],
    )


def _document(entries: list[dict], config: dict) -> dict:
    ordered = sorted(entries, key=_sort_key)
    identifiers = [entry["id"] for entry in ordered]
    if len(identifiers) != len(set(identifiers)):
        raise IndexError("índice produziria identidades duplicadas")
    locales = Counter(
        (
            entry["localization"]["language_path"],
            entry["localization"]["category"],
            entry["localization"]["type"],
        )
        for entry in ordered
    )
    configuration = {
        "source_root": config["source_root"],
        "public_root": config["public_root"],
        "index_path": config.get("intelligence", {}).get("index_path"),
    }
    return {
        "schema_version": INDEX_SCHEMA,
        "generation": {
            "generator": GENERATOR_ID,
            "version": GENERATOR_VERSION,
            "configuration_sha256": _fingerprint(configuration),
            "source_fingerprint": _fingerprint(
                [
                    {
                        "id": entry["id"],
                        "metadata": entry["metadata"]["path"],
                        "assets": [asset["hashes"] for asset in entry["assets"]],
                    }
                    for entry in ordered
                ]
            ),
        },
        "locales": [
            {
                "language_path": key[0],
                "category": key[1],
                "type": key[2],
                "publications": count,
            }
            for key, count in sorted(locales.items())
        ],
        "publications": ordered,
    }


def _valid_existing(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        value = _read_json(path)
    except IndexError:
        return None
    if (
        not isinstance(value, dict)
        or set(value) != {"schema_version", "generation", "locales", "publications"}
        or value.get("schema_version") != INDEX_SCHEMA
        or not isinstance(value.get("publications"), list)
    ):
        return None
    return value


def index_manifest_path(index_path: Path) -> Path:
    """Mantém o cartão sucinto imediatamente ao lado do índice descrito."""

    return index_path.with_name(f"{index_path.stem}.manifest{index_path.suffix}")


def write_index_manifest(index_path: Path) -> Path:
    """Materializa o mapa tipado, agnóstico de qualquer instância do índice."""

    target = index_manifest_path(index_path)
    _write_json_if_changed(target, INDEX_MANIFEST)
    return target


def _update_global_index_unlocked(
    source_root: Path,
    index_path: Path,
    config: dict,
    publication: Path | None = None,
) -> Path:
    """Atualiza uma publicação quando há cobertura íntegra; senão reconstrói."""

    root = source_root.resolve()
    target = index_path.resolve()
    if target != root and root not in target.parents:
        raise IndexError("índice global fora da raiz de publicações")
    all_metadata = _metadata_paths(root)
    existing = _valid_existing(target)
    expected_paths = {path.relative_to(root).as_posix() for path in all_metadata}
    existing_paths = (
        {
            str((entry.get("metadata") or {}).get("path") or "")
            for entry in existing["publications"]
        }
        if existing is not None
        else set()
    )
    incremental = publication is not None and existing is not None and existing_paths == expected_paths
    if incremental:
        selected = _metadata_paths(root, publication)
        if len(selected) != 1:
            raise IndexError("atualização incremental exige uma publicação")
        replacement = build_index_entry(selected[0], root, config)
        entries = [entry for entry in existing["publications"] if entry["id"] != replacement["id"]]
        entries.append(replacement)
    else:
        entries = [build_index_entry(path, root, config) for path in all_metadata]
    document = _document(entries, config)
    _write_json_if_changed(target, document)
    write_index_manifest(target)
    return target


def update_global_index(
    source_root: Path,
    index_path: Path,
    config: dict,
    publication: Path | None = None,
) -> Path:
    """Serializa atualizações concorrentes dentro do processo do downloader."""

    with _INDEX_LOCK:
        return _update_global_index_unlocked(
            source_root,
            index_path,
            config,
            publication,
        )


def generate_scope_index(
    source_root: Path,
    index_path: Path,
    config: dict,
    scope: Path,
) -> Path:
    entries = [
        build_index_entry(path, source_root.resolve(), config)
        for path in _metadata_paths(source_root, scope)
    ]
    document = _document(entries, config)
    _write_json_if_changed(index_path, document)
    write_index_manifest(index_path)
    return index_path


def configured_index_path(config: dict) -> Path:
    value = str((config.get("intelligence") or {}).get("index_path") or "")
    if not value:
        raise IndexError("intelligence.index_path ausente")
    return resolve_repository_path(value, REPOSITORY_ROOT)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera ou atualiza o índice global multilocalizado."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="executa antes o avaliador, respeitando a janela de 24 horas",
    )
    parser.add_argument(
        "--force-recalculate",
        action="store_true",
        help="propaga recálculo forçado ao avaliador usado por --analyze",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="propaga reset do diário global ao avaliador usado por --analyze --all",
    )
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--publication", type=Path)
    scope.add_argument("--scope", type=Path)
    scope.add_argument("--all", action="store_true")
    scope.add_argument("--manifest-only", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    reporter = PublicationReporter("Indexador global")
    try:
        arguments = _parser().parse_args(list(argv) if argv is not None else None)
        config = load_config(arguments.config)
        source_root = resolve_repository_path(config["source_root"], REPOSITORY_ROOT)
        output = (
            arguments.output.resolve()
            if arguments.output is not None
            else configured_index_path(config)
        )
        reporter.start(str(output))
        if arguments.force_recalculate and not arguments.analyze:
            raise IndexError("--force-recalculate exige --analyze")
        if arguments.reset and not (arguments.analyze and arguments.all):
            raise IndexError("--reset exige --analyze --all")
        if arguments.analyze:
            if arguments.manifest_only:
                raise IndexError("--analyze não se aplica a --manifest-only")
            analysis_target = source_root if arguments.all else (
                arguments.publication or arguments.scope
            )
            analyze_and_commit_scope(
                Path(analysis_target),
                source_root,
                config,
                reporter.child("Análise"),
                force_recalculate=arguments.force_recalculate,
                reset=arguments.reset,
            )
        manifest_output = None
        if arguments.manifest_only:
            manifest_output = write_index_manifest(output)
        elif arguments.scope is not None:
            if arguments.output is None:
                raise IndexError("--scope exige --output para não substituir o índice global")
            generate_scope_index(source_root, output, config, arguments.scope)
        else:
            update_global_index(
                source_root,
                output,
                config,
                publication=arguments.publication,
            )
        indexed = None if manifest_output else json.loads(output.read_text(encoding="utf-8"))
        summary = (
            {"manifesto": manifest_output, "schema": INDEX_MANIFEST_SCHEMA}
            if manifest_output
            else {
                "publicações": len(indexed.get("publications") or []),
                "arquivo": output,
                "fingerprint": str(
                    (indexed.get("generation") or {}).get("source_fingerprint") or "—"
                )[:16],
            }
        )
        reporter.result("Manifesto concluído" if manifest_output else "Índice concluído", summary)
        return 0
    except (IndexError, ContractError, OSError) as error:
        reporter.error("Índice", error)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
