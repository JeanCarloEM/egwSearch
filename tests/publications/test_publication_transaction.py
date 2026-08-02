# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(CONTRACT_ROOT))

from acquisition import (  # noqa: E402
    AcquisitionLedger,
    CatalogItem,
    CatalogSegment,
    build_source_v3,
    generate_epub,
    write_markdown_publication,
)
from publication_contract import hash_file, write_json_atomic  # noqa: E402
from publication_analysis import analyze_publication  # noqa: E402
from publication_index import update_global_index  # noqa: E402
from publication_transaction import (  # noqa: E402
    GitPublicationPublisher,
    PublicationTransactionError,
    validate_complete_publication,
)


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-c", "maintenance.auto=false", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _item() -> CatalogItem:
    return CatalogItem(
        remote_id="42",
        collection_id="fixture",
        collection_name="Fixture",
        author_name="Author",
        author_key="author",
        language_original="en",
        language="en",
        language_path="en",
        publication_type="books",
        title_original="Atomic Publication",
        title_normalized="Atomic Publication",
        public_url="https://example.test/book/42",
    )


def _materialize(root: Path, item: CatalogItem) -> Path:
    source_root = root / "src" / "publications"
    identity = item.publication_identity()
    directory = source_root / identity.relative_directory()
    directory.mkdir(parents=True)
    pdf = directory / identity.asset_name("pdf")
    pdf.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
    evidence = hash_file(pdf)
    metadata = build_source_v3(
        item,
        "completed",
        [
            {
                "format": "pdf",
                "url": "https://media2.egwwritings.org/pdf/fixture.pdf",
                "method": "native-download",
                "size": evidence.size,
                "hashes": evidence.as_dict(),
            }
        ],
    )
    write_json_atomic(directory / identity.metadata_name(), metadata)
    return source_root


def _index_config(source_root: Path) -> dict:
    return {
        "source_root": source_root.as_posix(),
        "public_root": "/publications",
        "authors": {"author": {"name": "Author"}},
        "intelligence": {"index_path": (source_root / "index.json").as_posix()},
    }


class PublicationTransactionTests(unittest.TestCase):
    def test_complete_publication_accepts_reversible_markdown_inside_epub(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            item = replace(
                _item(),
                segments=(
                    CatalogSegment(
                        remote_id="42.1",
                        url="https://example.test/read/42.1",
                        order=1,
                        title="Capítulo real",
                        html="<h1>Capítulo real</h1><p>Conteúdo.</p>",
                    ),
                ),
            )
            source_root = root / "src" / "publications"
            identity = item.publication_identity()
            directory = source_root / identity.relative_directory()
            markdown, evidence = write_markdown_publication(directory, item)
            epub = generate_epub(
                directory / identity.asset_name("epub", "derived"),
                item,
                markdown,
                accessed_at="2026-08-01T12:00:00+00:00",
            )
            epub_hashes = hash_file(epub)
            for record, path in zip(evidence, markdown, strict=True):
                record["path"] = (
                    f"{epub.name}!/META-INF/egwsearch-source/{path.name}"
                )
                path.unlink()
            metadata = build_source_v3(
                item,
                "completed",
                [
                    {
                        "format": "text",
                        "url": item.segments[0].url,
                        "method": "text-extraction",
                    }
                ],
                segments=evidence,
                derivations=[
                    {
                        "format": "epub",
                        "method": "local-conversion",
                        "path": epub.name,
                        "size": epub_hashes.size,
                        "hashes": epub_hashes.as_dict(),
                    }
                ],
            )
            write_json_atomic(directory / identity.metadata_name(), metadata)
            analyze_publication(directory, source_root)
            allowlist = validate_complete_publication(item, source_root, root)
            self.assertIn(epub.relative_to(root), allowlist)
            self.assertFalse(list(directory.rglob("*.md")))

    def test_commit_contains_exactly_one_publication_and_preserves_unrelated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _git(root, "init", "-b", "dev")
            _git(root, "config", "user.name", "Fixture")
            _git(root, "config", "user.email", "fixture@example.test")
            (root / ".gitignore").write_text("/constructor/.state/\n", encoding="utf-8")
            (root / "README.md").write_text("fixture\n", encoding="utf-8")
            _git(root, "add", "--", ".gitignore", "README.md")
            _git(root, "commit", "-m", "Inicializa fixture")

            item = _item()
            source_root = _materialize(root, item)
            directory = source_root / item.publication_identity().relative_directory()
            analyze_publication(directory, source_root)
            update_global_index(
                source_root,
                source_root / "index.json",
                _index_config(source_root),
                publication=directory,
            )
            (root / "unrelated.txt").write_text("preservar\n", encoding="utf-8")
            ledger = AcquisitionLedger(root / "constructor" / ".state" / "ledger.json")
            publisher = GitPublicationPublisher(
                root,
                source_root,
                root / "constructor" / ".state" / "locks" / "publication-git.lock",
            )
            allowlist = validate_complete_publication(item, source_root, root)
            commit = publisher.commit(item, allowlist, ledger)

            self.assertRegex(commit or "", r"^[0-9a-f]{40}$")
            committed = set(
                _git(root, "show", "--pretty=format:", "--name-only", commit).splitlines()
            )
            self.assertEqual(
                committed,
                {
                    *(path.as_posix() for path in allowlist),
                    "src/publications/index.json",
                },
            )
            self.assertIn("?? unrelated.txt", _git(root, "status", "--short"))
            self.assertEqual(ledger.get(item.stable_key())["commit"], commit)
            index = json.loads(
                (root / "src" / "publications" / "index.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(index["schema_version"], "publication-global-index/v1")
            self.assertEqual(index["publications"][0]["remote_id"], "42")
            self.assertIsNone(publisher.commit(item, allowlist, ledger))
            self.assertEqual(_git(root, "rev-list", "--count", "HEAD"), "2")

    def test_runtime_partial_blocks_completeness(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            item = _item()
            source_root = _materialize(root, item)
            directory = source_root / item.publication_identity().relative_directory()
            (directory / ".download.partial").write_bytes(b"partial")
            with self.assertRaises(PublicationTransactionError):
                validate_complete_publication(item, source_root, root)

    def test_preflight_blocks_preexisting_change_in_same_unit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _git(root, "init", "-b", "dev")
            _git(root, "config", "user.name", "Fixture")
            _git(root, "config", "user.email", "fixture@example.test")
            item = _item()
            source_root = _materialize(root, item)
            publisher = GitPublicationPublisher(
                root,
                source_root,
                root / "constructor" / ".state" / "locks" / "publication-git.lock",
            )
            with self.assertRaises(PublicationTransactionError):
                publisher.preflight(item)


if __name__ == "__main__":
    unittest.main()
