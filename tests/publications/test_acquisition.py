# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Testes offline dos contratos incrementais da FT-006."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
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
    restore_markdown_from_epub,
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
        "category_name": "Biblioteca dos Pioneiros Adventistas",
        "category": "pioneiros",
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

    def test_official_collection_category_becomes_uri_path_segment(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        items = parse_catalog_payload(
            fixture["collections"]["pt-br-pioneiros"],
            _collection("pt-br-pioneiros", "pt-BR", "Pioneiros"),
        )
        identity = items[0].publication_identity()
        self.assertEqual(identity.category, "pioneiros")
        self.assertEqual(
            identity.relative_directory().as_posix(),
            "pioneiros/alonzo-trevier-jones/pt-br/livros/estudos-sobre-a-fe",
        )
        metadata = build_source_v3(items[0], "completed", [{"format": "epub", "url": "https://example.test/a.epub"}])
        self.assertEqual(metadata["identity"]["category_original"], "Biblioteca dos Pioneiros Adventistas")
        self.assertEqual(metadata["identity"]["category"], "pioneiros")

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
        self.assertIn("Corpo **real**.", markdown)
        self.assertNotIn("Anterior", markdown)
        self.assertNotIn("Rodapé", markdown)

    def test_reader_heading_classes_and_emphasis_are_preserved(self) -> None:
        markdown = editorial_html_to_markdown(
            '<p class="h3" id="14389.102">2 - Estudos <em>sobre</em> a Fé</p>'
        )
        self.assertEqual(markdown, "### 2 - Estudos *sobre* a Fé\n")

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

    def test_generated_epub_embeds_canonical_cover_as_first_spine_item(self) -> None:
        from PIL import Image
        import zipfile

        item = self._item()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cover = root / "cover.png"
            Image.new("RGB", (320, 480), (20, 40, 60)).save(cover, format="PNG")
            paths, _evidence = write_markdown_publication(root, item)
            epub = generate_epub(root / "covered.epub", item, paths, cover_path=cover)
            cover_hash = hashlib.sha256(cover.read_bytes()).hexdigest()
            validate_generated_epub(
                epub,
                expected_sections=2,
                expected_cover_sha256=cover_hash,
            )
            with zipfile.ZipFile(epub) as archive:
                self.assertEqual(archive.read("OEBPS/cover.png"), cover.read_bytes())
                opf = archive.read("OEBPS/content.opf").decode("utf-8")
                cover_page = archive.read("OEBPS/cover.xhtml").decode("utf-8")
                provenance = archive.read("OEBPS/provenance.xhtml").decode("utf-8")
                self.assertLess(
                    opf.find('idref="cover-page"'),
                    opf.find('idref="section-0001"'),
                )
                self.assertGreater(
                    opf.find('idref="provenance"'),
                    opf.find('idref="section-0001"'),
                )
                self.assertIn("Nota de proveniência (não editorial)", provenance)
                self.assertIn(item.public_url, provenance)
                self.assertIn('@page{margin:0;padding:0}', cover_page)
                self.assertIn('epub:type="cover"', cover_page)
                self.assertIn('width="100%" height="100%"', cover_page)
                self.assertIn('preserveAspectRatio="xMidYMid slice"', cover_page)
                self.assertNotIn("<img", cover_page)
                self.assertNotIn("<p", cover_page)
            restored = restore_markdown_from_epub(epub, root / "restored")
            self.assertEqual(
                {path.name: path.read_bytes() for path in restored},
                {path.name: path.read_bytes() for path in paths},
            )

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
            self.assertFalse(list(source_root.rglob("*.md")))
            epub = next(source_root.rglob("*.derived.epub"))
            restored = restore_markdown_from_epub(epub, root / "restored")
            self.assertEqual(len(restored), 2)
            source_document = json.loads(
                next(source_root.rglob("*.source.json")).read_text(encoding="utf-8")
            )
            self.assertTrue(
                all("!/META-INF/egwsearch-source/" in record["path"] for record in source_document["segments"])
            )
            text_document = json.loads(
                next(source_root.rglob("0000-metadata.json")).read_text(encoding="utf-8")
            )
            self.assertEqual(text_document["reversible_epub"], epub.name)
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
