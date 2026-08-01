# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(CONTRACT_ROOT))

from acquisition import AcquisitionLedger, CatalogItem, build_source_v3  # noqa: E402
from publication_contract import hash_file, write_json_atomic  # noqa: E402
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


class PublicationTransactionTests(unittest.TestCase):
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
            self.assertEqual(committed, {path.as_posix() for path in allowlist})
            self.assertIn("?? unrelated.txt", _git(root, "status", "--short"))
            self.assertEqual(ledger.get(item.stable_key())["commit"], commit)

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
