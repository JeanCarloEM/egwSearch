# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Testes offline dos contratos incrementais da FT-006."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(MODULE_ROOT))

from acquisition import (  # noqa: E402
    AcquisitionLedger,
    CatalogItem,
    CatalogSegment,
    RateLimiter,
    RatePolicy,
    build_source_v3,
    canonical_author_key,
    canonical_language,
    editorial_html_to_markdown,
    generate_epub,
    ordered_segments,
    parse_catalog_payload,
    parse_retry_after,
    validate_generated_epub,
    write_markdown_publication,
)
from publication_contract import ContractError, hash_file, load_config  # noqa: E402
import baixar  # noqa: E402


FIXTURE = REPOSITORY_ROOT / "tests" / "fixtures" / "publications" / "pioneers.json"


def _collection(identifier: str, language: str, name: str) -> dict:
    return {
        "id": identifier,
        "name": name,
        "language": language,
        "type": "livros" if language.startswith("pt") else "books",
        "discover_authors": True,
    }


class IdentityAndCatalogTests(unittest.TestCase):
    def test_only_pt_br_and_en_are_eligible(self) -> None:
        self.assertEqual(canonical_language("pt_BR"), ("pt-BR", "pt-br"))
        self.assertEqual(canonical_language("en-GB"), ("en", "en"))
        with self.assertRaises(ContractError):
            canonical_language("es")

    def test_author_key_is_uri_safe_and_stable(self) -> None:
        self.assertEqual(canonical_author_key("J. N. Andrews"), "j-n-andrews")
        self.assertEqual(canonical_author_key("J. N. Andrews"), canonical_author_key("J. N. Andrews"))
        self.assertNotIn("..", canonical_author_key("../../evil"))

    def test_pioneer_fixture_preserves_multiple_authors_and_formats(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        items = parse_catalog_payload(
            fixture["collections"]["pt-br-pioneiros"],
            _collection(
                "pt-br-pioneiros",
                "pt-BR",
                "Biblioteca dos Pioneiros Adventistas",
            ),
        )
        self.assertEqual(len(items), 2)
        self.assertEqual(
            {item.author_key for item in items},
            {"alonzo-trevier-jones", "john-nevins-andrews"},
        )
        native = next(item for item in items if item.remote_id == "14391")
        self.assertEqual([asset.format for asset in native.assets], ["epub", "pdf"])

    def test_noneligible_catalog_item_is_rejected(self) -> None:
        payload = {
            "items": [
                {
                    "id": 1,
                    "title": "Obra",
                    "author": "Autor",
                    "language": "es",
                    "url": "https://text.egwwritings.org/book/b1",
                }
            ]
        }
        with self.assertRaises(ContractError):
            parse_catalog_payload(payload, _collection("fixture", "en", "Fixture"))

    def test_config_exposes_both_new_collections_and_conservative_defaults(self) -> None:
        config = load_config(REPOSITORY_ROOT / "config" / "publications.json")
        identifiers = {item["id"] for item in config["collections"]}
        self.assertIn("pt-br-pioneiros", identifiers)
        self.assertIn("en-pioneers", identifiers)
        self.assertEqual(config["download"]["workers"], 1)
        self.assertLessEqual(config["download"]["max_workers"], 2)
        source_root = REPOSITORY_ROOT / config["source_root"]
        self.assertNotIn(source_root, MODULE_ROOT.parents)
        self.assertTrue((MODULE_ROOT / "requirements.txt").is_file())
        self.assertFalse(
            (source_root / "egw" / "baixar.py").exists(),
            "automacao operacional nao pode integrar a raiz publica",
        )


class LedgerAndRateTests(unittest.TestCase):
    def test_ledger_persists_resume_state_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.json"
            ledger = AcquisitionLedger(path, now=lambda: "2026-07-26T00:00:00+00:00")
            ledger.transition("key", "processing", remote_id="1")
            reloaded = AcquisitionLedger(path)
            self.assertEqual(reloaded.get("key")["state"], "processing")
            reloaded.transition("key", "completed", sha256="a" * 64)
            self.assertEqual(AcquisitionLedger(path).get("key")["state"], "completed")

    def test_rate_limiter_applies_delay_and_jitter(self) -> None:
        clock_value = [0.0]
        sleeps: list[float] = []

        def sleep(value: float) -> None:
            sleeps.append(value)
            clock_value[0] += value

        limiter = RateLimiter(
            RatePolicy(delay_seconds=2, jitter_min_seconds=1, jitter_max_seconds=1),
            clock=lambda: clock_value[0],
            sleeper=sleep,
            random_uniform=lambda _low, _high: 1,
        )
        self.assertEqual(limiter.before_request(), 0)
        self.assertEqual(limiter.before_request(), 3)
        self.assertEqual(sleeps, [3])

    def test_retry_after_seconds_and_date_are_supported(self) -> None:
        self.assertEqual(parse_retry_after("17"), 17)
        now = datetime(2026, 7, 26, tzinfo=timezone.utc)
        self.assertEqual(
            parse_retry_after("Sun, 26 Jul 2026 00:00:12 GMT", now=now),
            12,
        )

    def test_attempt_limit_is_bounded(self) -> None:
        with self.assertRaises(ContractError):
            RatePolicy(max_attempts=4)


class TextAndEpubTests(unittest.TestCase):
    def _item(self) -> CatalogItem:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        return parse_catalog_payload(
            fixture["collections"]["pt-br-pioneiros"],
            _collection(
                "pt-br-pioneiros",
                "pt-BR",
                "Biblioteca dos Pioneiros Adventistas",
            ),
        )[0]

    def test_interface_is_excluded_and_hierarchy_preserved(self) -> None:
        markdown = editorial_html_to_markdown(
            "<nav>Anterior</nav><h2>Título</h2><p>Corpo <strong>real</strong>.</p>"
            "<footer>Rodapé</footer>"
        )
        self.assertIn("## Título", markdown)
        self.assertIn("Corpo real.", markdown)
        self.assertNotIn("Anterior", markdown)
        self.assertNotIn("Rodapé", markdown)

    def test_gap_or_duplicate_blocks_completion(self) -> None:
        segments = [
            CatalogSegment("1", "https://example.test/1", 1, "Um", "<p>Um</p>"),
            CatalogSegment("3", "https://example.test/3", 3, "Três", "<p>Três</p>"),
        ]
        with self.assertRaises(ContractError):
            ordered_segments(segments)
        with self.assertRaises(ContractError):
            ordered_segments([segments[0], segments[0]])

    def test_markdown_is_numbered_in_editorial_order(self) -> None:
        item = self._item()
        with tempfile.TemporaryDirectory() as temporary:
            paths, evidence = write_markdown_publication(Path(temporary), item)
            self.assertEqual([path.name[:4] for path in paths], ["0001", "0002"])
            self.assertEqual([entry["order"] for entry in evidence], [1, 2])
            self.assertNotIn("Interface", paths[0].read_text(encoding="utf-8"))

    def test_generated_epub_is_valid_and_deterministic(self) -> None:
        item = self._item()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths, _evidence = write_markdown_publication(root, item)
            first = generate_epub(root / "first.epub", item, paths)
            second = generate_epub(root / "second.epub", item, paths)
            validate_generated_epub(first, expected_sections=2)
            self.assertEqual(hash_file(first).sha256, hash_file(second).sha256)

    def test_metadata_distinguishes_original_and_local_derivative(self) -> None:
        item = self._item()
        document = build_source_v3(
            item,
            "completed",
            [
                {
                    "format": "text",
                    "url": item.segments[0].url,
                    "method": "text-extraction",
                }
            ],
            derivations=[
                {
                    "format": "epub",
                    "method": "local-conversion",
                    "path": "book.derived.epub",
                }
            ],
        )
        self.assertEqual(document["sources"][0]["method"], "text-extraction")
        self.assertEqual(document["derivations"][0]["method"], "local-conversion")
        self.assertNotIn("url", document["derivations"][0])

    def test_controlled_fixture_sample_is_idempotent_without_network(self) -> None:
        config = load_config(REPOSITORY_ROOT / "config" / "publications.json")
        collection = next(
            item
            for item in config["collections"]
            if item["id"] == "pt-br-pioneiros"
        )
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        payload = fixture["collections"]["pt-br-pioneiros"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_root = root / "publications"
            state_root = root / "state"
            first = baixar._process_collection(
                collection,
                config,
                source_root,
                state_root,
                None,
                limit=1,
                no_network=True,
                fixture_payload=payload,
            )
            self.assertEqual(first["extracted"], 2)
            self.assertEqual(first["converted"], 1)
            output_files = sorted(
                path for path in source_root.rglob("*") if path.is_file()
            )
            before = {
                path.relative_to(source_root).as_posix(): (
                    path.stat().st_mtime_ns,
                    hash_file(path).sha256,
                )
                for path in output_files
            }
            second = baixar._process_collection(
                collection,
                config,
                source_root,
                state_root,
                None,
                limit=1,
                no_network=True,
                fixture_payload=payload,
            )
            after = {
                path.relative_to(source_root).as_posix(): (
                    path.stat().st_mtime_ns,
                    hash_file(path).sha256,
                )
                for path in output_files
            }
            self.assertEqual(second["skipped"], 1)
            self.assertEqual(second["extracted"], 0)
            self.assertEqual(second["converted"], 0)
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
