# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Planeja e executa a migracao transacional do acervo legado.

O comando default e ``plan`` e nunca move arquivos. Aplicacao exige um plano
persistido, integralmente revalidado e acompanhado por journal atomico.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
if str(CONTRACT_ROOT) not in sys.path:
    sys.path.insert(0, str(CONTRACT_ROOT))

from publication_contract import (  # noqa: E402
    ContractError,
    DEFAULT_CONFIG_PATH,
    choose_variant_path,
    hash_file,
    load_config,
    publication_identity,
    read_source_records,
    resolve_repository_path,
    uri_slug,
    validate_file_signature,
    write_json_atomic,
)


PLAN_SCHEMA = "egw-publications-migration-plan/v1"
JOURNAL_SCHEMA = "egw-publications-migration-journal/v1"
DEFAULT_STATE_ROOT = REPOSITORY_ROOT / "constructor" / ".state" / "publications-migration"


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ContractError(f"path fora da raiz declarada: {path}") from error


def _legacy_title(path: Path) -> tuple[str, str] | None:
    if path.name.endswith(".source.json"):
        return path.name[: -len(".source.json")], "metadata"
    if path.suffix.casefold() in {".pdf", ".epub"}:
        return path.stem, path.suffix.casefold()[1:]
    return None


def _inventory_digest(entries: list[dict]) -> str:
    canonical = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _directory_digest(entries: list[dict]) -> str:
    canonical = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _plan_identity(plan_without_id: dict) -> str:
    canonical = json.dumps(
        plan_without_id,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _iter_legacy_files(source_root: Path) -> Iterable[tuple[str, str, str, Path]]:
    """Enumera somente arquivos planos no nivel legado conhecido."""

    for author_directory in sorted(source_root.iterdir(), key=lambda item: item.name.casefold()):
        if not author_directory.is_dir():
            continue
        for language_directory in sorted(
            author_directory.iterdir(), key=lambda item: item.name.casefold()
        ):
            if not language_directory.is_dir():
                continue
            for type_directory in sorted(
                language_directory.iterdir(), key=lambda item: item.name.casefold()
            ):
                if not type_directory.is_dir():
                    continue
                for candidate in sorted(
                    type_directory.iterdir(), key=lambda item: item.name.casefold()
                ):
                    if candidate.is_file():
                        yield (
                            author_directory.name,
                            language_directory.name,
                            type_directory.name,
                            candidate,
                        )


def _iter_canonical_directories(
    source_root: Path,
) -> Iterable[tuple[str, str, str, Path]]:
    for author_directory in sorted(source_root.iterdir(), key=lambda item: item.name.casefold()):
        if not author_directory.is_dir():
            continue
        for language_directory in sorted(
            author_directory.iterdir(), key=lambda item: item.name.casefold()
        ):
            if not language_directory.is_dir():
                continue
            for type_directory in sorted(
                language_directory.iterdir(), key=lambda item: item.name.casefold()
            ):
                if not type_directory.is_dir():
                    continue
                for candidate in sorted(
                    type_directory.iterdir(), key=lambda item: item.name.casefold()
                ):
                    if candidate.is_dir():
                        yield (
                            author_directory.name,
                            language_directory.name,
                            type_directory.name,
                            candidate,
                        )


def _canonical_kind(path: Path, acronym: str) -> str | None:
    if path.name == f"{acronym}.source.json":
        return "metadata"
    suffix = path.suffix.casefold()
    if suffix not in {".pdf", ".epub"}:
        return None
    stem = path.name[: -len(suffix)]
    if stem == acronym:
        return suffix[1:]
    variant = re.fullmatch(
        rf"{re.escape(acronym)}\.([0-9a-f]{{8,64}})",
        stem,
    )
    if variant and len(variant.group(1)) % 2 == 0:
        return suffix[1:]
    return None


def _build_canonical_plan(
    source_root: Path,
    directories: list[tuple[str, str, str, Path]],
) -> dict:
    inventory: list[dict] = []
    planned_groups: list[dict] = []
    actions: list[dict] = []
    problems: list[dict] = []
    descriptors: list[dict] = []
    destinations: dict[str, list[str]] = {}

    for author, language, publication_type, directory in directories:
        source_directory = _relative(directory, source_root)
        try:
            slug = uri_slug(directory.name)
        except ContractError as error:
            problems.append(
                {
                    "code": "INVALID_IDENTITY",
                    "group": source_directory,
                    "detail": str(error),
                }
            )
            continue
        title = None
        if directory.name == slug:
            metadata_names = sorted(
                candidate.name[: -len(".source.json")]
                for candidate in directory.iterdir()
                if candidate.is_file() and candidate.name.endswith(".source.json")
            )
            acronym = metadata_names[0] if len(metadata_names) == 1 else ""
        else:
            try:
                identity = publication_identity(
                    author,
                    language,
                    publication_type,
                    directory.name,
                )
            except ContractError as error:
                problems.append(
                    {
                        "code": "INVALID_IDENTITY",
                        "group": source_directory,
                        "detail": str(error),
                    }
                )
                continue
            title = identity.title
            slug = identity.route_slug
            acronym = identity.acronym
        target_directory = Path(author, language, publication_type, slug).as_posix()
        descriptor = {
            "author": author,
            "language": language,
            "type": publication_type,
            "directory": directory,
            "source_directory": source_directory,
            "target_directory": target_directory,
            "title": title,
            "slug": slug,
            "acronym": acronym,
        }
        descriptors.append(descriptor)
        destinations.setdefault(target_directory.casefold(), []).append(source_directory)

    colliding_directories: set[str] = set()
    for target, sources in sorted(destinations.items()):
        if len(sources) > 1:
            colliding_directories.update(sources)
            problems.append(
                {
                    "code": "SLUG_COLLISION",
                    "target": target,
                    "groups": sorted(sources, key=str.casefold),
                }
            )

    for descriptor in descriptors:
        directory = descriptor["directory"]
        source_directory = descriptor["source_directory"]
        acronym = descriptor["acronym"]
        by_kind: dict[str, list[Path]] = {}
        file_hashes: dict[str, object] = {}
        for candidate in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
            relative = _relative(candidate, source_root)
            if not candidate.is_file():
                problems.append({"code": "UNSUPPORTED_CANONICAL_ENTRY", "path": relative})
                continue
            kind = _canonical_kind(candidate, acronym)
            if kind is None:
                problems.append({"code": "INVALID_CANONICAL_NAME", "path": relative})
                continue
            hashes = hash_file(candidate)
            file_hashes[relative] = hashes
            by_kind.setdefault(kind, []).append(candidate)
            inventory.append(
                {
                    "path": relative,
                    "kind": kind,
                    "size": hashes.size,
                    "sha256": hashes.sha256,
                }
            )
            if kind in {"pdf", "epub"}:
                try:
                    validate_file_signature(candidate, kind)
                except ContractError as error:
                    problems.append(
                        {
                            "code": "INVALID_FORMAT",
                            "path": relative,
                            "detail": str(error),
                        }
                    )
        metadata_paths = by_kind.get("metadata", [])
        assets = {
            kind: paths
            for kind, paths in by_kind.items()
            if kind in {"pdf", "epub"}
        }
        if not assets:
            problems.append(
                {"code": "GROUP_WITHOUT_ASSET", "group": source_directory}
            )
        if len(metadata_paths) != 1:
            problems.append(
                {
                    "code": "GROUP_WITHOUT_SINGLE_METADATA",
                    "group": source_directory,
                    "count": len(metadata_paths),
                }
            )
        elif assets:
            try:
                records = read_source_records(metadata_paths[0])
                records_by_format: dict[str, list[dict]] = {}
                for record in records:
                    records_by_format.setdefault(record["format"], []).append(record)
                for publication_format, paths in assets.items():
                    candidates = records_by_format.get(publication_format, [])
                    expected_hashes = {
                        record.get("hashes", {}).get("sha256")
                        for record in candidates
                        if record.get("hashes", {}).get("sha256")
                    }
                    for asset in paths:
                        relative = _relative(asset, source_root)
                        actual = file_hashes[relative].sha256
                        if not candidates:
                            problems.append(
                                {
                                    "code": "ASSET_WITHOUT_METADATA_SOURCE",
                                    "path": relative,
                                    "format": publication_format,
                                }
                            )
                        elif expected_hashes and actual not in expected_hashes:
                            problems.append(
                                {
                                    "code": "METADATA_HASH_MISMATCH",
                                    "path": relative,
                                    "actual_sha256": actual,
                                    "metadata_sha256": sorted(expected_hashes),
                                }
                            )
                for publication_format in records_by_format:
                    if publication_format not in assets:
                        problems.append(
                            {
                                "code": "METADATA_SOURCE_WITHOUT_ASSET",
                                "path": _relative(metadata_paths[0], source_root),
                                "format": publication_format,
                            }
                        )
            except ContractError as error:
                problems.append(
                    {
                        "code": "INVALID_METADATA",
                        "path": _relative(metadata_paths[0], source_root),
                        "detail": str(error),
                    }
                )
        group_actions: list[dict] = []
        if (
            source_directory != descriptor["target_directory"]
            and source_directory not in colliding_directories
        ):
            target_root = source_root / descriptor["target_directory"]
            target_is_source = target_root.exists() and os.path.samefile(
                target_root,
                directory,
            )
            if target_root.exists() and not target_is_source:
                problems.append(
                    {
                        "code": "SLUG_TARGET_EXISTS",
                        "group": source_directory,
                        "target": descriptor["target_directory"],
                    }
                )
            else:
                entries = []
                for candidate in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
                    relative = _relative(candidate, source_root)
                    hashes = file_hashes.get(relative)
                    if hashes is not None:
                        entries.append(
                            {
                                "name": candidate.name,
                                "kind": _canonical_kind(candidate, acronym),
                                "size": hashes.size,
                                "sha256": hashes.sha256,
                            }
                        )
                action = {
                    "source": source_directory,
                    "target": descriptor["target_directory"],
                    "kind": "directory",
                    "size": sum(entry["size"] for entry in entries),
                    "sha256": _directory_digest(entries),
                    "entries": entries,
                    "disposition": "rename-directory",
                }
                actions.append(action)
                group_actions.append(action)
        planned_groups.append(
            {
                "identity": {
                    "author": descriptor["author"],
                    "language": descriptor["language"],
                    "type": descriptor["type"],
                    "title": descriptor["title"],
                    "slug": descriptor["slug"],
                    "acronym": acronym,
                    "directory": descriptor["target_directory"],
                },
                "source_directory": source_directory,
                "actions": group_actions,
            }
        )

    inventory.sort(key=lambda item: item["path"].casefold())
    actions.sort(key=lambda item: item["source"].casefold())
    problems.sort(
        key=lambda item: (
            item["code"],
            str(item.get("path", item.get("group", ""))).casefold(),
        )
    )
    plan = {
        "schema": PLAN_SCHEMA,
        "source_root": _relative(source_root, REPOSITORY_ROOT),
        "inventory": {
            "files": len(inventory),
            "bytes": sum(item["size"] for item in inventory),
            "sha256": _inventory_digest(inventory),
            "entries": inventory,
        },
        "groups": planned_groups,
        "actions": actions,
        "problems": problems,
        "summary": {
            "groups": len(planned_groups),
            "actions": len(actions),
            "moves": sum(
                len(action.get("entries", [None]))
                for action in actions
            ),
            "deduplications": 0,
            "problems": len(problems),
        },
    }
    plan["plan_id"] = _plan_identity(plan)
    return plan


def build_plan(source_root: Path) -> dict:
    """Produz plano reprodutivel e diagnosticos sem alterar o acervo."""

    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise ContractError(f"raiz de publicacoes ausente: {source_root}")
    legacy_files = list(_iter_legacy_files(source_root))
    canonical_directories = list(_iter_canonical_directories(source_root))
    if legacy_files and canonical_directories:
        raise ContractError("layout misto legado/canônico exige rollback ou reparo")
    if canonical_directories:
        return _build_canonical_plan(source_root, canonical_directories)
    groups: dict[tuple[str, str, str, str], list[tuple[Path, str]]] = {}
    problems: list[dict] = []
    for author, language, publication_type, candidate in legacy_files:
        parsed = _legacy_title(candidate)
        if parsed is None:
            problems.append(
                {
                    "code": "UNSUPPORTED_LEGACY_FILE",
                    "path": _relative(candidate, source_root),
                }
            )
            continue
        title, kind = parsed
        key = (author, language, publication_type, title)
        groups.setdefault(key, []).append((candidate, kind))

    inventory: list[dict] = []
    planned_groups: list[dict] = []
    actions: list[dict] = []
    for key in sorted(groups, key=lambda item: tuple(part.casefold() for part in item)):
        author, language, publication_type, title = key
        try:
            identity = publication_identity(author, language, publication_type, title)
        except ContractError as error:
            problems.append(
                {
                    "code": "INVALID_IDENTITY",
                    "group": "/".join(key),
                    "detail": str(error),
                }
            )
            continue
        files = groups[key]
        by_kind: dict[str, list[Path]] = {}
        file_hashes: dict[str, object] = {}
        for path, kind in files:
            by_kind.setdefault(kind, []).append(path)
            hashes = hash_file(path)
            file_hashes[_relative(path, source_root)] = hashes
            inventory.append(
                {
                    "path": _relative(path, source_root),
                    "kind": kind,
                    "size": hashes.size,
                    "sha256": hashes.sha256,
                }
            )
            if kind in {"pdf", "epub"}:
                try:
                    validate_file_signature(path, kind)
                except ContractError as error:
                    problems.append(
                        {
                            "code": "INVALID_FORMAT",
                            "path": _relative(path, source_root),
                            "detail": str(error),
                        }
                    )
        for kind, paths in by_kind.items():
            if len(paths) > 1:
                problems.append(
                    {
                        "code": "DUPLICATE_LEGACY_KIND",
                        "group": "/".join(key),
                        "kind": kind,
                        "paths": [_relative(path, source_root) for path in paths],
                    }
                )
        assets = {
            kind: paths[0]
            for kind, paths in by_kind.items()
            if kind in {"pdf", "epub"} and len(paths) == 1
        }
        metadata_paths = by_kind.get("metadata", [])
        if not assets:
            problems.append({"code": "GROUP_WITHOUT_ASSET", "group": "/".join(key)})
        if len(metadata_paths) != 1:
            problems.append(
                {
                    "code": "GROUP_WITHOUT_SINGLE_METADATA",
                    "group": "/".join(key),
                    "count": len(metadata_paths),
                }
            )
        elif assets:
            try:
                records = read_source_records(metadata_paths[0])
                records_by_format: dict[str, list[dict]] = {}
                for record in records:
                    records_by_format.setdefault(record["format"], []).append(record)
                for publication_format, asset in assets.items():
                    candidates = records_by_format.get(publication_format, [])
                    if not candidates:
                        problems.append(
                            {
                                "code": "ASSET_WITHOUT_METADATA_SOURCE",
                                "path": _relative(asset, source_root),
                                "format": publication_format,
                            }
                        )
                        continue
                    expected_hashes = {
                        record.get("hashes", {}).get("sha256")
                        for record in candidates
                        if record.get("hashes", {}).get("sha256")
                    }
                    actual = file_hashes[_relative(asset, source_root)].sha256
                    if expected_hashes and actual not in expected_hashes:
                        problems.append(
                            {
                                "code": "METADATA_HASH_MISMATCH",
                                "path": _relative(asset, source_root),
                                "actual_sha256": actual,
                                "metadata_sha256": sorted(expected_hashes),
                            }
                        )
                for publication_format in records_by_format:
                    if publication_format not in assets:
                        problems.append(
                            {
                                "code": "METADATA_SOURCE_WITHOUT_ASSET",
                                "path": _relative(metadata_paths[0], source_root),
                                "format": publication_format,
                            }
                        )
            except ContractError as error:
                problems.append(
                    {
                        "code": "INVALID_METADATA",
                        "path": _relative(metadata_paths[0], source_root),
                        "detail": str(error),
                    }
                )

        group_actions = []
        for path, kind in sorted(files, key=lambda item: item[0].name.casefold()):
            hashes = file_hashes[_relative(path, source_root)]
            target_directory = source_root / identity.relative_directory()
            target_name = (
                identity.metadata_name()
                if kind == "metadata"
                else identity.asset_name(kind)
            )
            target, duplicate = choose_variant_path(target_directory / target_name, hashes.sha256)
            action = {
                "source": _relative(path, source_root),
                "target": _relative(target, source_root),
                "kind": kind,
                "size": hashes.size,
                "sha256": hashes.sha256,
                "disposition": "deduplicate" if duplicate else "move",
            }
            actions.append(action)
            group_actions.append(action)
        planned_groups.append(
            {
                "identity": {
                    "author": identity.author,
                    "language": identity.language,
                    "type": identity.publication_type,
                    "title": identity.title,
                    "acronym": identity.acronym,
                    "directory": identity.relative_directory().as_posix(),
                },
                "actions": group_actions,
            }
        )

    inventory.sort(key=lambda item: item["path"].casefold())
    actions.sort(key=lambda item: item["source"].casefold())
    problems.sort(
        key=lambda item: (
            item["code"],
            str(item.get("path", item.get("group", ""))).casefold(),
        )
    )
    plan = {
        "schema": PLAN_SCHEMA,
        "source_root": _relative(source_root, REPOSITORY_ROOT),
        "inventory": {
            "files": len(inventory),
            "bytes": sum(item["size"] for item in inventory),
            "sha256": _inventory_digest(inventory),
            "entries": inventory,
        },
        "groups": planned_groups,
        "actions": actions,
        "problems": problems,
        "summary": {
            "groups": len(planned_groups),
            "actions": len(actions),
            "moves": sum(action["disposition"] == "move" for action in actions),
            "deduplications": sum(
                action["disposition"] == "deduplicate" for action in actions
            ),
            "problems": len(problems),
        },
    }
    plan["plan_id"] = _plan_identity(plan)
    return plan


def load_plan(path: Path) -> dict:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"plano invalido: {path}: {error}") from error
    if plan.get("schema") != PLAN_SCHEMA or not isinstance(plan.get("plan_id"), str):
        raise ContractError("schema de plano invalido")
    expected = dict(plan)
    expected.pop("plan_id")
    if _plan_identity(expected) != plan["plan_id"]:
        raise ContractError("identidade causal do plano divergente")
    return plan


def _resolve_inside(root: Path, relative: str) -> Path:
    if Path(relative).is_absolute():
        raise ContractError(f"path absoluto no plano: {relative}")
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ContractError(f"path escapa da raiz: {relative}")
    return candidate


def _resolve_inside_preserving_name(root: Path, relative: str) -> Path:
    if Path(relative).is_absolute():
        raise ContractError(f"path absoluto no plano: {relative}")
    canonical_root = root.resolve()
    candidate = canonical_root / Path(relative)
    resolved = candidate.resolve()
    if resolved != canonical_root and canonical_root not in resolved.parents:
        raise ContractError(f"path escapa da raiz: {relative}")
    return candidate


def _verify_action_source(source_root: Path, action: dict) -> Path:
    source = _resolve_inside(source_root, action["source"])
    if not source.is_file():
        raise ContractError(f"origem ausente: {action['source']}")
    hashes = hash_file(source)
    if hashes.size != action["size"] or hashes.sha256 != action["sha256"]:
        raise ContractError(f"origem divergente do plano: {action['source']}")
    return source


def _verify_directory_at(directory: Path, action: dict) -> None:
    if not directory.is_dir():
        raise ContractError(f"diretorio ausente: {directory}")
    actual_names = sorted(
        candidate.name
        for candidate in directory.iterdir()
        if candidate.is_file()
    )
    expected_names = sorted(entry["name"] for entry in action["entries"])
    if actual_names != expected_names or any(
        not candidate.is_file()
        for candidate in directory.iterdir()
    ):
        raise ContractError(f"conteudo de diretorio divergente: {directory}")
    verified_entries = []
    for entry in sorted(action["entries"], key=lambda item: item["name"].casefold()):
        candidate = directory / entry["name"]
        hashes = hash_file(candidate)
        if hashes.size != entry["size"] or hashes.sha256 != entry["sha256"]:
            raise ContractError(f"arquivo de diretorio divergente: {candidate}")
        verified_entries.append(
            {
                "name": entry["name"],
                "kind": entry["kind"],
                "size": hashes.size,
                "sha256": hashes.sha256,
            }
        )
    if (
        sum(entry["size"] for entry in verified_entries) != action["size"]
        or _directory_digest(verified_entries) != action["sha256"]
    ):
        raise ContractError(f"identidade de diretorio divergente: {directory}")


def _temporary_directory(source: Path, source_relative: str) -> Path:
    digest = hashlib.sha256(source_relative.encode("utf-8")).hexdigest()[:16]
    return source.with_name(f".slug-migration-{digest}")


def _exists_with_exact_name(path: Path) -> bool:
    return path.parent.is_dir() and any(
        candidate.name == path.name
        for candidate in path.parent.iterdir()
    )


def _journal_path(state_root: Path, plan_id: str) -> Path:
    return state_root / plan_id / "journal.json"


def _load_journal(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"journal invalido: {path}: {error}") from error
    if data.get("schema") != JOURNAL_SCHEMA:
        raise ContractError("schema de journal invalido")
    return data


def rollback(journal_path: Path) -> dict:
    """Reverte registros em ordem inversa sem tocar path alheio."""

    journal = _load_journal(journal_path)
    if journal["status"] == "finalized":
        raise ContractError("journal finalizado nao possui quarentena para rollback")
    source_root = resolve_repository_path(journal["source_root"], REPOSITORY_ROOT)
    cleanup_directories: set[Path] = set()
    for record in reversed(journal["records"]):
        if record["disposition"] == "rename-directory":
            source = _resolve_inside_preserving_name(source_root, record["source"])
            target = _resolve_inside_preserving_name(source_root, record["target"])
            temporary = Path(record["temporary"]).resolve()
            if _exists_with_exact_name(source):
                _verify_directory_at(source, record)
            elif _exists_with_exact_name(temporary):
                _verify_directory_at(temporary, record)
                os.replace(temporary, source)
            elif _exists_with_exact_name(target):
                _verify_directory_at(target, record)
                if temporary.exists():
                    raise ContractError(f"temporario de rollback ja existe: {temporary}")
                os.replace(target, temporary)
                os.replace(temporary, source)
            else:
                raise ContractError(
                    f"rollback sem diretorio fonte, temporario ou alvo: {record['source']}"
                )
            _verify_directory_at(source, record)
            record["current"] = str(source)
            record["status"] = "rolled_back"
            continue
        source = _resolve_inside(source_root, record["source"])
        current = Path(record["current"]).resolve()
        if record["disposition"] == "move":
            cleanup_directories.add(current.parent)
        if source.exists() and not current.exists():
            record["status"] = "rolled_back"
            continue
        if not current.exists():
            raise ContractError(f"rollback sem origem nem arquivo corrente: {current}")
        source.parent.mkdir(parents=True, exist_ok=True)
        if source.exists():
            if hash_file(source).sha256 != record["sha256"]:
                raise ContractError(f"rollback colide com origem divergente: {source}")
            if hash_file(current).sha256 != record["sha256"]:
                raise ContractError(f"rollback colide com corrente divergente: {current}")
            current.unlink()
        else:
            os.replace(current, source)
        record["status"] = "rolled_back"
    for directory in sorted(
        cleanup_directories,
        key=lambda item: (len(item.parts), str(item).casefold()),
        reverse=True,
    ):
        if source_root in directory.parents and directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    journal["status"] = "rolled_back"
    write_json_atomic(journal_path, journal)
    return journal


def apply_plan(plan_path: Path, state_root: Path = DEFAULT_STATE_ROOT) -> Path:
    """Aplica movimentos com journal e rollback automatico em falha."""

    plan = load_plan(plan_path)
    if plan["problems"]:
        raise ContractError(
            f"plano possui {len(plan['problems'])} problema(s) bloqueante(s)"
        )
    source_root = resolve_repository_path(plan["source_root"], REPOSITORY_ROOT)
    current = build_plan(source_root)
    if current["plan_id"] != plan["plan_id"]:
        raise ContractError("estado atual diverge do plano persistido")
    state_root = state_root.resolve()
    journal_path = _journal_path(state_root, plan["plan_id"])
    if journal_path.exists():
        existing = _load_journal(journal_path)
        if existing["status"] == "complete":
            return journal_path
        if existing["status"] != "rolled_back":
            raise ContractError(f"journal exige acao: {journal_path}")
    journal = {
        "schema": JOURNAL_SCHEMA,
        "plan_id": plan["plan_id"],
        "source_root": plan["source_root"],
        "status": "applying",
        "records": [],
    }
    write_json_atomic(journal_path, journal)
    quarantine = journal_path.parent / "quarantine"
    try:
        for action in plan["actions"]:
            if action["disposition"] == "rename-directory":
                source = _resolve_inside_preserving_name(source_root, action["source"])
                target = _resolve_inside_preserving_name(source_root, action["target"])
                _verify_directory_at(source, action)
                if target.exists() and not os.path.samefile(target, source):
                    raise ContractError(f"destino apareceu depois do plano: {target}")
                temporary = _temporary_directory(source, action["source"])
                if temporary.exists():
                    raise ContractError(f"temporario de migracao ja existe: {temporary}")
                record = {
                    "source": action["source"],
                    "target": action["target"],
                    "temporary": str(temporary),
                    "current": str(source),
                    "disposition": action["disposition"],
                    "entries": action["entries"],
                    "size": action["size"],
                    "sha256": action["sha256"],
                    "status": "pending",
                }
                journal["records"].append(record)
                write_json_atomic(journal_path, journal)
                os.replace(source, temporary)
                record["current"] = str(temporary)
                record["status"] = "temporary"
                write_json_atomic(journal_path, journal)
                if target.exists():
                    raise ContractError(f"destino apareceu durante migracao: {target}")
                os.replace(temporary, target)
                record["current"] = str(target)
                record["status"] = "moved"
                write_json_atomic(journal_path, journal)
                continue
            source = _verify_action_source(source_root, action)
            target = _resolve_inside(source_root, action["target"])
            current_path = (
                target
                if action["disposition"] == "move"
                else quarantine / action["source"]
            )
            record = {
                "source": action["source"],
                "target": action["target"],
                "current": str(current_path),
                "disposition": action["disposition"],
                "sha256": action["sha256"],
                "status": "pending",
            }
            journal["records"].append(record)
            write_json_atomic(journal_path, journal)
            if action["disposition"] == "move":
                if target.exists():
                    raise ContractError(f"destino apareceu depois do plano: {target}")
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, target)
            elif action["disposition"] == "deduplicate":
                if not target.is_file() or hash_file(target).sha256 != action["sha256"]:
                    raise ContractError(f"duplicata alvo divergente: {target}")
                current_path.parent.mkdir(parents=True, exist_ok=True)
                os.replace(source, current_path)
            else:
                raise ContractError(f"disposition invalida: {action['disposition']}")
            record["status"] = "moved"
            write_json_atomic(journal_path, journal)
        for record in journal["records"]:
            if record["disposition"] == "rename-directory":
                target = _resolve_inside_preserving_name(source_root, record["target"])
                _verify_directory_at(target, record)
            elif record["disposition"] == "move":
                target = _resolve_inside(source_root, record["target"])
                if hash_file(target).sha256 != record["sha256"]:
                    raise ContractError(f"hash pos-movimento divergente: {target}")
        source_directories = sorted(
            {
                _resolve_inside(source_root, action["source"]).parent
                for action in plan["actions"]
                if (
                    action["disposition"] == "move"
                    and Path(action["source"]).parent
                    != Path(action["target"]).parent
                    and Path(action["source"]).parent
                    not in Path(action["target"]).parent.parents
                )
            },
            key=lambda item: (len(item.parts), str(item).casefold()),
            reverse=True,
        )
        for directory in source_directories:
            if not directory.is_dir():
                continue
            if any(directory.iterdir()):
                raise ContractError(f"diretorio de origem nao ficou vazio: {directory}")
            directory.rmdir()
        journal["status"] = "complete"
        write_json_atomic(journal_path, journal)
        return journal_path
    except Exception:
        rollback(journal_path)
        raise


def finalize(journal_path: Path) -> dict:
    """Descarta somente quarentena validada de journal concluido."""

    journal = _load_journal(journal_path)
    if journal["status"] != "complete":
        raise ContractError("finalize exige journal complete")
    source_root = resolve_repository_path(journal["source_root"], REPOSITORY_ROOT)
    for record in journal["records"]:
        if record["disposition"] == "rename-directory":
            target = _resolve_inside_preserving_name(source_root, record["target"])
            _verify_directory_at(target, record)
        elif record["disposition"] == "move":
            target = _resolve_inside(source_root, record["target"])
            if not target.is_file() or hash_file(target).sha256 != record["sha256"]:
                raise ContractError(f"destino final divergente: {target}")
    quarantine = journal_path.parent / "quarantine"
    if quarantine.exists():
        shutil.rmtree(quarantine)
    journal["status"] = "finalized"
    write_json_atomic(journal_path, journal)
    return journal


def _summary(plan: dict) -> str:
    return json.dumps(
        {
            "plan_id": plan["plan_id"],
            **plan["summary"],
            "files": plan["inventory"]["files"],
            "bytes": plan["inventory"]["bytes"],
            "inventory_sha256": plan["inventory"]["sha256"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Migra publicacoes legadas com plano e rollback.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    subparsers = parser.add_subparsers(dest="command")
    plan_parser = subparsers.add_parser("plan", help="gera plano sem mover arquivos")
    plan_parser.add_argument("--output")
    apply_parser = subparsers.add_parser("apply", help="aplica um plano persistido")
    apply_parser.add_argument("--plan", required=True)
    apply_parser.add_argument("--state-root", default=str(DEFAULT_STATE_ROOT))
    rollback_parser = subparsers.add_parser("rollback", help="reverte um journal")
    rollback_parser.add_argument("--journal", required=True)
    finalize_parser = subparsers.add_parser("finalize", help="finaliza quarentena validada")
    finalize_parser.add_argument("--journal", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    command = arguments.command or "plan"
    try:
        config = load_config(arguments.config)
        source_root = resolve_repository_path(config["source_root"], REPOSITORY_ROOT)
        if command == "plan":
            plan = build_plan(source_root)
            output = getattr(arguments, "output", None)
            if output:
                write_json_atomic(Path(output).resolve(), plan)
            print(_summary(plan))
            return 3 if plan["problems"] else 0
        if command == "apply":
            journal = apply_plan(
                Path(arguments.plan).resolve(),
                Path(arguments.state_root).resolve(),
            )
            print(json.dumps({"status": "complete", "journal": str(journal)}))
            return 0
        if command == "rollback":
            journal = rollback(Path(arguments.journal).resolve())
            print(json.dumps({"status": journal["status"]}))
            return 0
        if command == "finalize":
            journal = finalize(Path(arguments.journal).resolve())
            print(json.dumps({"status": journal["status"]}))
            return 0
        parser.error(f"comando desconhecido: {command}")
    except ContractError as error:
        print(f"ERRO_CONTRATO: {error}", file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("CANCELADO", file=sys.stderr)
        return 130
    except OSError as error:
        print(f"ERRO_OPERACIONAL: {error}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
