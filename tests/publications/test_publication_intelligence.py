# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Testes offline do índice global e da análise estrutural da FT-013."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(MODULE_ROOT))

from acquisition import CatalogAsset, CatalogItem, build_source_v3, generate_epub  # noqa: E402
from publication_analysis import (  # noqa: E402
    AnalysisError,
    CATALOG_SCHEMA,
    LEARNING_SCHEMA,
    MANIFEST_SCHEMA,
    _measure_experiment,
    _reference_model,
    _safe_zip_entries,
    analyze_publication,
    analyze_scope,
    inspect_asset,
    learning_path_for,
    manifest_path_for,
)
from publication_contract import hash_file, write_json_atomic  # noqa: E402
import publication_index  # noqa: E402


class SafeEpubEntryTests(unittest.TestCase):
    def test_empty_zip_record_is_ignored_without_relaxing_validation(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            epub = Path(temporary) / "empty-record.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("", b"")
                archive.writestr("mimetype", b"application/epub+zip")
            with zipfile.ZipFile(epub) as archive:
                self.assertEqual(
                    [entry.filename for entry in _safe_zip_entries(archive)],
                    ["mimetype"],
                )

    def test_zip_traversal_remains_rejected_with_entry_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            epub = Path(temporary) / "traversal.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("../escape.xhtml", b"unsafe")
            with zipfile.ZipFile(epub) as archive:
                with self.assertRaisesRegex(AnalysisError, "escape.xhtml"):
                    _safe_zip_entries(archive)

    def test_malformed_epub_is_measured_as_structural_only(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            epub = Path(temporary) / "malformed.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("mimetype", b"application/epub+zip")
                archive.writestr("", b"<p>orphan content</p>")
                archive.writestr(
                    "META-INF/container.xml",
                    b'<?xml version="1.0"?><container><rootfiles>'
                    b'<rootfile full-path="missing.opf"/></rootfiles></container>',
                )
            report = inspect_asset(epub)
            self.assertEqual(report["parser"]["selected"], "binary-epub-structure")
            self.assertFalse(report["_model"]["complete"])
            self.assertEqual(report["structure"]["empty_zip_entries"], 1)
            self.assertIn("EPUB sem pacote OCF", report["limitations"][0])


def _config(root: Path) -> dict:
    return {
        "schema_version": 4,
        "source_root": root.as_posix(),
        "public_root": "/publications",
        "runtime_state_root": "constructor/.state/fixture",
        "authors": {"egw": {"name": "Ellen G. White"}},
        "collections": [
            {
                "id": "fixture",
                "name": "Fixture",
                "category_name": "EGW Writings",
                "category": "egw",
                "catalog_url": "https://text.egwwritings.org/allCollection/en/4",
                "language": "en",
                "type": "books",
                "default_author_key": "egw",
                "default_author_name": "Ellen G. White",
            }
        ],
        "download": {},
        "transaction": {"branch": "dev", "commit_per_publication": False},
        "intelligence": {"index_path": (root / "index.json").as_posix()},
    }


def _item(remote_id: str = "42", title: str = "Structured Book") -> CatalogItem:
    return CatalogItem(
        remote_id=remote_id,
        collection_id="fixture",
        collection_name="Fixture",
        author_name="Ellen G. White",
        author_key="egw",
        language_original="en",
        language="en",
        language_path="en",
        publication_type="books",
        title_original=title,
        title_normalized=title,
        public_url=f"https://text.egwwritings.org/book/b{remote_id}",
        category_name="EGW Writings",
        category_path="egw",
    )


def _materialize(root: Path, item: CatalogItem) -> tuple[Path, Path, Path]:
    identity = item.publication_identity()
    directory = root / identity.relative_directory()
    text = directory / "text"
    text.mkdir(parents=True)
    markdown = text / "0001-chapter.md"
    markdown.write_text(
        "# Chapter 1\n\n## A topic\n\nFirst paragraph. Second sentence.\n\n"
        "Third paragraph with enough structure for analysis.\n",
        encoding="utf-8",
    )
    epub = generate_epub(
        directory / identity.asset_name("epub"),
        item,
        [markdown],
        accessed_at="2026-08-02T00:00:00+00:00",
    )
    pdf = directory / identity.asset_name("pdf")
    pdf.write_bytes(b"%PDF-1.7\n1 0 obj <</Type /Page>> endobj\n%%EOF")
    epub_hashes = hash_file(epub)
    pdf_hashes = hash_file(pdf)
    native = (
        CatalogAsset("epub", "https://media2.egwwritings.org/epub/en_fixture.epub"),
        CatalogAsset("pdf", "https://media2.egwwritings.org/pdf/en_fixture.pdf"),
    )
    completed_item = CatalogItem(**{**item.__dict__, "assets": native})
    metadata = build_source_v3(
        completed_item,
        "completed",
        [
            {
                "format": "epub",
                "url": native[0].url,
                "size": epub_hashes.size,
                "hashes": epub_hashes.as_dict(),
            },
            {
                "format": "pdf",
                "url": native[1].url,
                "size": pdf_hashes.size,
                "hashes": pdf_hashes.as_dict(),
            },
        ],
    )
    write_json_atomic(directory / identity.metadata_name(), metadata)
    return directory, epub, pdf


class PublicationIntelligenceTests(unittest.TestCase):
    def test_epub_and_pdf_receive_explainable_idempotent_manifests(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, epub, pdf = _materialize(root, _item())
            manifests = analyze_publication(directory, root)
            self.assertEqual(manifests, [manifest_path_for(epub), manifest_path_for(pdf)])
            epub_manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
            self.assertEqual(epub_manifest["schema_version"], MANIFEST_SCHEMA)
            self.assertEqual(epub_manifest["asset"]["hashes"], hash_file(epub).as_dict())
            self.assertTrue(epub_manifest["publication"]["generated_epub"])
            self.assertGreater(epub_manifest["structure"]["headings"], 0)
            self.assertEqual(epub_manifest["catalog"]["schema"], CATALOG_SCHEMA)
            experiment_ids = {entry["method"] for entry in epub_manifest["experiments"]}
            self.assertTrue({"paragraph", "sentence", "regex-structural"} <= experiment_ids)
            self.assertNotIn("strategies", epub_manifest)
            self.assertNotIn("benefit", json.dumps(epub_manifest, ensure_ascii=False))
            self.assertNotIn("risk", json.dumps(epub_manifest, ensure_ascii=False))
            self.assertTrue(
                all(
                    entry["proof"]["reference_tokens_sha256"]
                    == epub_manifest["reference"]["tokens_sha256"]
                    for entry in epub_manifest["experiments"]
                )
            )
            pdf_manifest = json.loads(manifests[1].read_text(encoding="utf-8"))
            self.assertIn(pdf_manifest["parser"]["selected"], {"pypdfium2", "binary-pdf-structure"})
            learning = json.loads(learning_path_for(root).read_text(encoding="utf-8"))
            self.assertEqual(learning["schema_version"], LEARNING_SCHEMA)
            self.assertGreaterEqual(learning["manifests"], 2)
            before = {path: path.stat().st_mtime_ns for path in manifests}
            learning_before = learning_path_for(root).stat().st_mtime_ns
            time.sleep(0.01)
            analyze_publication(directory, root)
            self.assertEqual(before, {path: path.stat().st_mtime_ns for path in manifests})
            self.assertEqual(learning_before, learning_path_for(root).stat().st_mtime_ns)

    def test_real_experiment_measures_boundaries_noise_and_cross_page_continuity(self) -> None:
        blocks = [
            {"kind": "heading", "text": "Capítulo 1", "page": 1},
            {"kind": "paragraph", "text": "Uma frase atravessa a página sem perder conteúdo.", "page": 1},
            {"kind": "paragraph", "text": "Segundo parágrafo completo.", "page": 2},
        ]
        pages = [
            ["Capítulo 1", "Uma frase atravessa a página sem perder conteúdo."],
            ["Segundo parágrafo completo."],
        ]
        model = _reference_model(
            blocks,
            pages,
            complete=True,
            noise=[{"signature": "a" * 64, "position": -1, "occurrences": 2}],
            cross_page=[{"from": 1, "to": 2, "proof": "b" * 64}],
        )
        paragraph = _measure_experiment(
            "paragraph",
            [block["text"] for block in blocks],
            {"boundary": "parsed-block"},
            "paragraph",
            model,
        )
        self.assertEqual(paragraph["status"], "passed")
        self.assertEqual(paragraph["metrics"]["lost_tokens"], 0)
        self.assertEqual(paragraph["metrics"]["duplicated_tokens"], 0)
        self.assertEqual(paragraph["metrics"]["accuracy_ppm"], 1_000_000)
        page = _measure_experiment(
            "page-layout",
            model["pages"],
            {"boundary": "physical-page"},
            "page",
            model,
        )
        self.assertEqual(page["status"], "rejected")
        self.assertIn("page-break-crosses-unit", page["diagnostics"])

    def test_scope_can_target_asset_publication_subtree_or_corpus(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, epub, _pdf = _materialize(root, _item())
            self.assertEqual(len(analyze_scope(epub, root)), 1)
            self.assertEqual(len(analyze_scope(directory, root)), 2)
            self.assertEqual(len(analyze_scope(root / "egw", root)), 2)
            self.assertEqual(len(analyze_scope(root, root)), 2)

    def test_resume_reuses_only_verified_current_manifests(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, epub, _pdf = _materialize(root, _item())
            analyze_publication(directory, root)
            with patch("publication_analysis.inspect_asset") as inspector:
                self.assertEqual(
                    len(analyze_scope(root, root, reuse_existing=True)),
                    2,
                )
            inspector.assert_not_called()
            epub.write_bytes(epub.read_bytes() + b"changed")
            with patch(
                "publication_analysis.inspect_asset",
                wraps=inspect_asset,
            ) as inspector:
                analyze_scope(root, root, reuse_existing=True)
            self.assertEqual(inspector.call_count, 1)

    def test_global_index_preserves_public_urls_hashes_and_formative_boundary(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, _epub, _pdf = _materialize(root, _item())
            analyze_publication(directory, root)
            config = _config(root)
            target = root / "index.json"
            publication_index.update_global_index(root, target, config)
            document = json.loads(target.read_text(encoding="utf-8"))
            manifest = json.loads(
                publication_index.index_manifest_path(target).read_text(encoding="utf-8")
            )
            self.assertEqual(document["schema_version"], publication_index.INDEX_SCHEMA)
            self.assertEqual(len(document["publications"]), 1)
            entry = document["publications"][0]
            self.assertEqual(entry["formative_state"], "available")
            self.assertEqual(
                set(entry["formative_data"]), {"book", "urls", "global_hashes"}
            )
            self.assertEqual(
                [value["format"] for value in entry["formative_data"]["global_hashes"]],
                ["pdf", "epub"],
            )
            self.assertTrue(all(asset["url"].startswith("/publications/") for asset in entry["assets"]))
            self.assertTrue(all(asset["chunking_manifest"] for asset in entry["assets"]))
            self.assertEqual(
                manifest["schema_version"], publication_index.INDEX_MANIFEST_SCHEMA
            )
            self.assertEqual(manifest["describes"], publication_index.INDEX_SCHEMA)
            self.assertEqual(manifest["root"]["publications"], "publication[]")
            self.assertEqual(manifest["types"]["asset"]["format"], "pdf|epub")
            self.assertNotIn("publications", manifest)
            self.assertNotIn("totals", manifest)
            self.assertNotIn("index", manifest)

    def test_incremental_index_reuses_shared_entry_builder(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, _epub, _pdf = _materialize(root, _item())
            analyze_publication(directory, root)
            config = _config(root)
            target = root / "index.json"
            publication_index.update_global_index(root, target, config)
            with patch.object(
                publication_index,
                "build_index_entry",
                wraps=publication_index.build_index_entry,
            ) as builder:
                publication_index.update_global_index(
                    root,
                    target,
                    config,
                    publication=directory,
                )
            self.assertEqual(builder.call_count, 1)

    def test_index_manifest_is_agnostic_to_index_state_and_quantity(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            index = Path(temporary) / "index.json"
            manifest = publication_index.write_index_manifest(index)
            first = manifest.read_bytes()
            self.assertFalse(index.exists())

            index.write_text('{"publications": [1, 2, 3]}', encoding="utf-8")
            publication_index.write_index_manifest(index)
            self.assertEqual(manifest.read_bytes(), first)
            document = json.loads(first)
            self.assertNotIn("totals", document)
            self.assertNotIn("index", document)
            self.assertEqual(document["root"]["publications"], "publication[]")

    def test_local_derivative_is_not_promoted_to_formative_original(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            item = _item("77", "Online Only")
            directory, epub, pdf = _materialize(root, item)
            pdf.unlink()
            identity = item.publication_identity()
            evidence = hash_file(epub)
            metadata = build_source_v3(
                item,
                "completed",
                [
                    {
                        "format": "text",
                        "url": "https://text.egwwritings.org/read/77.1",
                        "method": "text-extraction",
                        "size": 10,
                        "hashes": {"sha256": "a" * 64},
                    }
                ],
                derivations=[
                    {
                        "format": "epub",
                        "method": "local-conversion",
                        "path": epub.name,
                        "size": evidence.size,
                        "hashes": evidence.as_dict(),
                    }
                ],
            )
            write_json_atomic(directory / identity.metadata_name(), metadata)
            analyze_publication(directory, root)
            config = _config(root)
            publication_index.update_global_index(root, root / "index.json", config)
            entry = json.loads((root / "index.json").read_text(encoding="utf-8"))[
                "publications"
            ][0]
            self.assertEqual(
                entry["formative_state"], "not-applicable-local-derivation"
            )
            self.assertIsNone(entry["formative_data"])


if __name__ == "__main__":
    unittest.main()
