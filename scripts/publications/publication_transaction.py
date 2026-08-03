# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Validação, progresso retomável e commit atômico de uma publicação."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
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


MANIFEST_SCHEMA = "publication-chunking-analysis/v2"
PROGRESS_SCHEMA = "publication-global-progress/v1"
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
        reset: bool = False,
    ) -> None:
        self.path = path.resolve()
        self.tool = tool
        self.scope = scope
        self.fingerprint = fingerprint
        self.order = list(order)
        if len(self.order) != len(set(self.order)):
            raise PublicationTransactionError("diário global possui ordem duplicada")
        if reset:
            self.path.unlink(missing_ok=True)
        self.document = self._load()

    @property
    def next_index(self) -> int:
        return int(self.document["next_index"])

    def _initial(self) -> dict:
        return {
            "schema_version": PROGRESS_SCHEMA,
            "tool": self.tool,
            "scope": self.scope,
            "fingerprint": self.fingerprint,
            "order": self.order,
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
        required = {
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
        if not isinstance(document, dict):
            raise PublicationTransactionError(
                f"diário global incompatível; use reset explícito: {self.path}"
            )
        stored_order = document.get("order")
        next_index = document.get("next_index")
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
            or document.get("fingerprint") != self.fingerprint
            or not isinstance(stored_order, list)
            or not all(isinstance(value, str) and value for value in stored_order)
            or not isinstance(next_index, int)
            or next_index < 0
            or next_index > len(stored_order)
            or not order_compatible
        ):
            raise PublicationTransactionError(
                f"diário global incompatível; use reset explícito: {self.path}"
            )
        appended = [value for value in self.order if value not in set(stored_order)]
        self.order = [*stored_order, *appended]
        if appended:
            document["order"] = self.order
            document["status"] = "running"
            _write_json_atomic(self.path, document)
        return document

    def record(self, position: int, identity: str, phase: str) -> None:
        """Atualiza a fase corrente sem avançar o limite confirmado."""

        if position < self.next_index or position >= len(self.order):
            raise PublicationTransactionError("posição inválida no diário global")
        if self.order[position] != identity:
            raise PublicationTransactionError("identidade divergente no diário global")
        self.document["current"] = {
            "position": position,
            "identity": identity,
            "phase": phase,
        }
        self.document["status"] = "running"
        _write_json_atomic(self.path, self.document)

    def confirm(self, position: int, identity: str, *, commit: str | None = None) -> None:
        """Avança somente a próxima unidade e persiste a prova de confirmação."""

        if position != self.next_index or self.order[position] != identity:
            raise PublicationTransactionError("avanço não contíguo no diário global")
        self.document["next_index"] = position + 1
        self.document["current"] = None
        self.document["last_confirmed"] = {
            "position": position,
            "identity": identity,
            "commit": commit,
        }
        self.document["status"] = (
            "completed" if position + 1 == len(self.order) else "running"
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

    editorial_assets = sorted(
        path
        for path in referenced
        if path.suffix.casefold() in {".epub", ".pdf"}
    )
    if not editorial_assets:
        raise PublicationTransactionError("publicação sem EPUB/PDF analisável")
    for asset in editorial_assets if require_intelligence else []:
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
            or not isinstance(manifest.get("experiments"), list)
            or not isinstance(manifest.get("reference"), dict)
            or not isinstance(manifest.get("recommendation"), dict)
            or not isinstance(manifest.get("catalog"), dict)
        ):
            raise PublicationTransactionError(
                f"manifesto de chunking divergente: {asset.name}"
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
        staged = _nul_paths(_git(self.repository_root, ["diff", "--cached", "--name-only", "-z"]).stdout)
        if staged:
            raise PublicationTransactionError("índice Git já contém alterações alheias")

    def preflight(self, item: CatalogItem, *, resume: bool = False) -> None:
        self._validate_repository()
        directory = self.source_root / item.publication_identity().relative_directory()
        relative = directory.relative_to(self.repository_root)
        source_relative = self.source_root.relative_to(self.repository_root)
        dirty = _status_paths(self.repository_root, source_relative)
        unit_prefix = f"{relative.as_posix()}/"
        globals_relative = {
            path.relative_to(self.repository_root).as_posix()
            for path in self.global_paths
        }
        unit_dirty = {
            path for path in dirty if path == relative.as_posix() or path.startswith(unit_prefix)
        }
        global_dirty = dirty & globals_relative
        unrelated = dirty - unit_dirty - global_dirty
        if unrelated:
            raise PublicationTransactionError(
                "outra publicação possui alterações: " + ", ".join(sorted(unrelated))
            )
        if not resume and (unit_dirty or global_dirty):
            raise PublicationTransactionError(
                "unidade possui alterações anteriores; preservar e resolver antes da coleta"
            )

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
