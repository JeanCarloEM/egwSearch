# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Testes transacionais do migrador, sempre sobre fixtures temporarias."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MIGRATOR_PATH = REPOSITORY_ROOT / "constructor" / "publications" / "migrate.py"
SPEC = importlib.util.spec_from_file_location("egw_migrate", MIGRATOR_PATH)
assert SPEC and SPEC.loader
migrate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(migrate)


class MigrationTests(unittest.TestCase):
    def _fixture(self, root: Path, include_metadata: bool = True) -> Path:
        source_root = root / "src" / "publications"
        legacy = source_root / "egw" / "pt-br" / "livros"
        legacy.mkdir(parents=True)
        pdf = legacy / "Atos Dos Apóstolos.pdf"
        pdf.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
        hashes = migrate.hash_file(pdf)
        if include_metadata:
            (legacy / "Atos Dos Apóstolos.source.json").write_text(
                json.dumps(
                    {
                        "https://media2.egwwritings.org/pdf/pt_AA.pdf": {
                            "acesso": 1746942924,
                            "sha256": hashes.sha256,
                        }
                    }
                ),
                encoding="utf-8",
            )
        return source_root

    def test_plan_is_deterministic_and_dry_run(self) -> None:
        state_root = REPOSITORY_ROOT / "constructor" / ".state"
        state_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=state_root) as temporary:
            source_root = self._fixture(Path(temporary))
            before = sorted(
                path.relative_to(source_root).as_posix()
                for path in source_root.rglob("*")
                if path.is_file()
            )
            first = migrate.build_plan(source_root)
            second = migrate.build_plan(source_root)
            after = sorted(
                path.relative_to(source_root).as_posix()
                for path in source_root.rglob("*")
                if path.is_file()
            )
            self.assertEqual(first, second)
            self.assertEqual(before, after)
            self.assertEqual(first["summary"]["problems"], 0)
            self.assertEqual(first["summary"]["actions"], 2)
            targets = {action["target"] for action in first["actions"]}
            self.assertIn(
                "egw/pt-br/livros/Atos Dos Apóstolos/ada.pdf",
                targets,
            )
            self.assertIn(
                "egw/pt-br/livros/Atos Dos Apóstolos/ada.source.json",
                targets,
            )

    def test_apply_and_rollback_preserve_bytes(self) -> None:
        state_root = REPOSITORY_ROOT / "constructor" / ".state"
        state_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=state_root) as temporary:
            root = Path(temporary)
            source_root = self._fixture(root)
            plan = migrate.build_plan(source_root)
            plan_path = root / "plan.json"
            migrate.write_json_atomic(plan_path, plan)

            journal_path = migrate.apply_plan(plan_path, root / ".state")
            canonical = (
                source_root
                / "egw"
                / "pt-br"
                / "livros"
                / "Atos Dos Apóstolos"
                / "ada.pdf"
            )
            self.assertTrue(canonical.is_file())
            expected_hash = next(
                action["sha256"]
                for action in plan["actions"]
                if action["kind"] == "pdf"
            )
            self.assertEqual(migrate.hash_file(canonical).sha256, expected_hash)
            migrate.rollback(journal_path)
            legacy = (
                source_root
                / "egw"
                / "pt-br"
                / "livros"
                / "Atos Dos Apóstolos.pdf"
            )
            self.assertTrue(legacy.is_file())
            self.assertEqual(migrate.hash_file(legacy).sha256, expected_hash)

    def test_orphan_asset_blocks_apply(self) -> None:
        state_root = REPOSITORY_ROOT / "constructor" / ".state"
        state_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=state_root) as temporary:
            plan = migrate.build_plan(self._fixture(Path(temporary), include_metadata=False))
            self.assertGreater(plan["summary"]["problems"], 0)
            self.assertIn(
                "GROUP_WITHOUT_SINGLE_METADATA",
                {problem["code"] for problem in plan["problems"]},
            )


if __name__ == "__main__":
    unittest.main()
