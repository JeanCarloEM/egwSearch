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
from unittest import mock


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
                "geral/egw/pt-br/livros/atos-dos-apostolos/ada.pdf",
                targets,
            )
            self.assertIn(
                "geral/egw/pt-br/livros/atos-dos-apostolos/ada.source.json",
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
                / "geral"
                / "egw"
                / "pt-br"
                / "livros"
                / "atos-dos-apostolos"
                / "ada.pdf"
            )
            self.assertTrue(canonical.is_file())
            expected_hash = next(
                action["sha256"]
                for action in plan["actions"]
                if action["kind"] == "pdf"
            )
            self.assertEqual(migrate.hash_file(canonical).sha256, expected_hash)
            post_plan = migrate.build_plan(source_root)
            self.assertEqual(post_plan["summary"]["groups"], 1)
            self.assertEqual(post_plan["summary"]["actions"], 0)
            self.assertEqual(post_plan["summary"]["problems"], 0)
            self.assertEqual(post_plan["inventory"]["files"], 2)
            self.assertEqual(post_plan, migrate.build_plan(source_root))
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

    def test_journal_failure_after_move_rolls_back_pending_record(self) -> None:
        state_root = REPOSITORY_ROOT / "constructor" / ".state"
        state_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=state_root) as temporary:
            root = Path(temporary)
            source_root = self._fixture(root)
            plan = migrate.build_plan(source_root)
            plan_path = root / "plan.json"
            migrate.write_json_atomic(plan_path, plan)
            original_write = migrate.write_json_atomic
            calls = 0

            def fail_after_first_move(path: Path, data: dict) -> None:
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise PermissionError("fixture: replace bloqueado")
                original_write(path, data)

            with mock.patch.object(
                migrate,
                "write_json_atomic",
                side_effect=fail_after_first_move,
            ):
                with self.assertRaises(PermissionError):
                    migrate.apply_plan(plan_path, root / ".state")

            legacy = (
                source_root
                / "egw"
                / "pt-br"
                / "livros"
                / "Atos Dos Apóstolos.pdf"
            )
            canonical = (
                source_root
                / "egw"
                / "pt-br"
                / "livros"
                / "atos-dos-apostolos"
                / "ada.pdf"
            )
            self.assertTrue(legacy.is_file())
            self.assertFalse(canonical.exists())

    def test_existing_title_directory_is_renamed_to_slug_and_rollback_restores_it(
        self,
    ) -> None:
        state_root = REPOSITORY_ROOT / "constructor" / ".state"
        state_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=state_root) as temporary:
            root = Path(temporary)
            source_root = root / "src" / "publications"
            title_directory = (
                source_root
                / "egw"
                / "pt-br"
                / "devocionais"
                / "A Maravilhosa Graça de Deus"
            )
            title_directory.mkdir(parents=True)
            pdf = title_directory / "amgdd.pdf"
            pdf.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
            hashes = migrate.hash_file(pdf)
            (title_directory / "amgdd.source.json").write_text(
                json.dumps(
                    {
                        "https://media2.egwwritings.org/pdf/pt_AG.pdf": {
                            "acesso": 1746942924,
                            "sha256": hashes.sha256,
                        }
                    }
                ),
                encoding="utf-8",
            )
            plan = migrate.build_plan(source_root)
            self.assertEqual(plan["summary"]["actions"], 1)
            self.assertEqual(plan["summary"]["moves"], 2)
            self.assertEqual(plan["summary"]["problems"], 0)
            plan_path = root / "slug-plan.json"
            migrate.write_json_atomic(plan_path, plan)

            journal_path = migrate.apply_plan(plan_path, root / ".state")
            slug_directory = (
                source_root
                / "geral"
                / "egw"
                / "pt-br"
                / "devocionais"
                / "a-maravilhosa-graca-de-deus"
            )
            self.assertFalse(title_directory.exists())
            self.assertTrue((slug_directory / "amgdd.pdf").is_file())
            post_plan = migrate.build_plan(source_root)
            self.assertEqual(post_plan["summary"]["actions"], 0)
            self.assertEqual(post_plan["summary"]["problems"], 0)

            migrate.rollback(journal_path)
            self.assertTrue((title_directory / "amgdd.pdf").is_file())
            self.assertFalse(slug_directory.exists())

    def test_case_only_directory_rename_uses_temporary_hop(self) -> None:
        state_root = REPOSITORY_ROOT / "constructor" / ".state"
        state_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=state_root) as temporary:
            root = Path(temporary)
            source_root = root / "src" / "publications"
            title_directory = (
                source_root / "egw" / "en-us" / "books" / "Education"
            )
            title_directory.mkdir(parents=True)
            pdf = title_directory / "education.pdf"
            pdf.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
            hashes = migrate.hash_file(pdf)
            (title_directory / "education.source.json").write_text(
                json.dumps(
                    {
                        "https://media2.egwwritings.org/pdf/en_ED.pdf": {
                            "acesso": 1746942924,
                            "sha256": hashes.sha256,
                        }
                    }
                ),
                encoding="utf-8",
            )
            plan = migrate.build_plan(source_root)
            self.assertEqual(plan["summary"]["actions"], 1)
            self.assertEqual(plan["summary"]["problems"], 0)
            plan_path = root / "case-plan.json"
            migrate.write_json_atomic(plan_path, plan)

            journal_path = migrate.apply_plan(plan_path, root / ".state")
            target_parent = source_root / "geral" / "egw" / "en-us" / "books"
            names = {candidate.name for candidate in target_parent.iterdir()}
            self.assertNotIn("Education", names)
            self.assertIn("education", names)
            migrate.rollback(journal_path)
            names = {candidate.name for candidate in title_directory.parent.iterdir()}
            self.assertIn("Education", names)
            self.assertNotIn("education", names)

    def test_slug_collision_blocks_apply(self) -> None:
        state_root = REPOSITORY_ROOT / "constructor" / ".state"
        state_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=state_root) as temporary:
            source_root = Path(temporary) / "src" / "publications"
            base = source_root / "egw" / "pt-br" / "livros"
            for title in ("Café", "Cafe"):
                group = base / title
                group.mkdir(parents=True)
                pdf = group / "cafe.pdf"
                pdf.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
                hashes = migrate.hash_file(pdf)
                (group / "cafe.source.json").write_text(
                    json.dumps(
                        {
                            "https://media2.egwwritings.org/pdf/pt_CAFE.pdf": {
                                "acesso": 1746942924,
                                "sha256": hashes.sha256,
                            }
                        }
                    ),
                    encoding="utf-8",
                )
            plan = migrate.build_plan(source_root)
            self.assertIn(
                "SLUG_COLLISION",
                {problem["code"] for problem in plan["problems"]},
            )


if __name__ == "__main__":
    unittest.main()
