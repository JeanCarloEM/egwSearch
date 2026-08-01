# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Validação e commit atômico, opt-in, de uma única publicação."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Iterable

from acquisition import AcquisitionLedger, CatalogItem
from publication_contract import (
    ContractError,
    REPOSITORY_ROOT,
    hash_file,
    validate_file_signature,
)


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
        candidate = (directory / relative).resolve()
        if not _inside(candidate, directory) or not candidate.is_file():
            raise PublicationTransactionError("segmento ausente ou fora da unidade")
        if hash_file(candidate).sha256 != expected_hash:
            raise PublicationTransactionError("hash de segmento divergente")
        referenced.add(candidate)

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
        referenced.add(candidate)

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


class GitPublicationPublisher:
    """Serializa staging/commit sem absorver a worktree do desenvolvedor."""

    def __init__(
        self,
        repository_root: Path,
        source_root: Path,
        lock_path: Path,
        branch: str = "dev",
    ) -> None:
        self.repository_root = repository_root.resolve()
        self.source_root = source_root.resolve()
        self.lock_path = lock_path.resolve()
        self.branch = branch

    def _validate_repository(self) -> None:
        inside = _git(self.repository_root, ["rev-parse", "--is-inside-work-tree"]).stdout.strip()
        if inside != b"true":
            raise PublicationTransactionError("diretório não é repositório Git")
        branch = _git(self.repository_root, ["branch", "--show-current"]).stdout.decode().strip()
        if branch != self.branch:
            raise PublicationTransactionError(f"commit exige branch {self.branch}")
        staged = _nul_paths(_git(self.repository_root, ["diff", "--cached", "--name-only", "-z"]).stdout)
        if staged:
            raise PublicationTransactionError("índice Git já contém alterações alheias")

    def preflight(self, item: CatalogItem, *, resume: bool = False) -> None:
        self._validate_repository()
        directory = self.source_root / item.publication_identity().relative_directory()
        if not directory.exists():
            return
        relative = directory.relative_to(self.repository_root)
        dirty = _status_paths(self.repository_root, relative)
        if dirty and not resume:
            raise PublicationTransactionError(
                "unidade possui alterações anteriores; preservar e resolver antes da coleta"
            )

    def commit(
        self,
        item: CatalogItem,
        paths: list[Path],
        ledger: AcquisitionLedger,
    ) -> str | None:
        self._validate_repository()
        allowed = {path.as_posix() for path in paths}
        runtime_relative = self.lock_path.parent.parent.relative_to(self.repository_root).as_posix()
        if any(path == runtime_relative or path.startswith(f"{runtime_relative}/") for path in allowed):
            raise PublicationTransactionError("allowlist contém estado de runtime")
        directory = self.source_root / item.publication_identity().relative_directory()
        relative_directory = directory.relative_to(self.repository_root)
        changed = _status_paths(self.repository_root, relative_directory)
        if not changed:
            return None
        if not changed.issubset(allowed):
            raise PublicationTransactionError(
                f"alteração fora da allowlist: {', '.join(sorted(changed - allowed))}"
            )
        key = item.stable_key()
        with _exclusive_lock(self.lock_path):
            created_commit: str | None = None
            try:
                self._validate_repository()
                locked_changed = _status_paths(self.repository_root, relative_directory)
                if locked_changed != changed:
                    raise PublicationTransactionError(
                        "unidade mudou enquanto aguardava finalização Git"
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
                    _git(
                        self.repository_root,
                        ["restore", "--staged", "--", *sorted(changed)],
                        check=False,
                    )
                    ledger.transition(key, "completed", git_state="commit_pending")
                raise
