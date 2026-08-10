# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Testes offline do índice global e da análise estrutural da FT-013."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(MODULE_ROOT))

from acquisition import (  # noqa: E402
    CatalogAsset,
    CatalogItem,
    CatalogSegment,
    build_source_v3,
    generate_epub,
)
from publication_analysis import (  # noqa: E402
    AnalysisError,
    CATALOG_SCHEMA,
    LEARNING_SCHEMA,
    MANIFEST_SCHEMA,
    _measure_experiment,
    _measure_semantic_experiment,
    _reference_model,
    _semantic_groups,
    _safe_zip_entries,
    analyze_publication,
    analyze_and_commit_scope,
    analyze_scope,
    inspect_asset,
    learning_path_for,
    manifest_path_for,
)
from publication_contract import ContractError, hash_file, write_json_atomic  # noqa: E402
from publication_transaction import validate_complete_publication  # noqa: E402
from structured_content import write_structured_artifact  # noqa: E402
import publication_index  # noqa: E402
import baixar  # noqa: E402


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
        "transaction": {"branch": "dev", "commit_per_publication": True},
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


def _structured_item(model: str, remote_id: str) -> CatalogItem:
    segments_by_model = {
        "scripture": [
            '<p data-book="Genesis" data-chapter="1" data-verse="1">In the beginning.</p>',
            '<p data-book="Genesis" data-chapter="1" data-verse="2">The earth was without form.</p>',
            '<p data-book="Genesis" data-chapter="2" data-verse="1">Thus the heavens were finished.</p>',
            '<p data-book="Psalms" data-chapter="1" data-verse="1">Blessed is the man.</p>',
        ],
        "lexical": [
            '<h4>(1) α, alpha</h4><p>First letter and lexical definition.</p><p>Genesis 1:1</p>',
            '<h4>(2) β, beta</h4><p>Second letter and lexical definition.</p><p>Romans 1:1</p>',
        ],
        "concordance": [
            '<h4>(1) α, alpha</h4><p>α Genesis 1:1</p><p>α Romans 1:1</p>',
            '<h4>(2) β, beta</h4><p>β Psalms 1:1</p>',
        ],
    }
    title = f"{model.title()} Fixture"
    return CatalogItem(
        remote_id=remote_id,
        collection_id=f"fixture-{model}",
        collection_name="Structured Fixture",
        author_name="Source tradition",
        author_key="source-tradition",
        language_original="en",
        language="en",
        language_path="en",
        publication_type="bible" if model == "scripture" else model,
        title_original=title,
        title_normalized=title,
        public_url=f"https://example.test/book/b{remote_id}",
        category_name="Reference",
        category_path="reference",
        segments=tuple(
            CatalogSegment(
                remote_id=str(index),
                url=f"https://example.test/read/{remote_id}.{index}",
                order=index,
                title=f"Unit {index}",
                html=html,
            )
            for index, html in enumerate(segments_by_model[model], 1)
        ),
        content_model=model,
        content_options={"collection": "BODY", "script": "Latn"},
    )


def _materialize_structured(root: Path, model: str, remote_id: str = "420") -> tuple[Path, Path, CatalogItem]:
    item = _structured_item(model, remote_id)
    identity = item.publication_identity()
    directory = root / identity.relative_directory()
    directory.mkdir(parents=True)
    structured, derivation = write_structured_artifact(directory, item)
    if model == "lexical":
        document = json.loads(structured.read_text(encoding="utf-8"))
        first = document["entries"][sorted(document["entries"])[0]]
        first["translations"] = {"pt-BR": ["alfa"]}
        first["relations"] = [{"type": "next", "target": "2"}]
        payload = {"meta": document["meta"], "entries": document["entries"]}
        document["proof"]["content_sha256"] = hashlib.sha256(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        write_json_atomic(structured, document)
        evidence = hash_file(structured)
        derivation["size"] = evidence.size
        derivation["hashes"] = evidence.as_dict()
    metadata = build_source_v3(
        item,
        "completed",
        [
            {
                "format": "text",
                "url": f"https://example.test/read/{remote_id}",
                "method": "fixture",
                "size": 1,
                "hashes": {"sha256": "a" * 64},
            }
        ],
        derivations=[derivation],
    )
    write_json_atomic(directory / identity.metadata_name(), metadata)
    return directory, structured, item


class PublicationIntelligenceTests(unittest.TestCase):
    def test_structured_domains_use_only_natural_semantic_units(self) -> None:
        expected = {
            "scripture": (["scripture-verse", "scripture-chapter", "scripture-book"], 4),
            "lexical": (["lexical-entry"], 2),
            "concordance": (["concordance-entry"], 2),
        }
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            for position, (model, (methods, units)) in enumerate(expected.items(), 1):
                with self.subTest(model=model):
                    directory, structured, _item_value = _materialize_structured(
                        root, model, str(420 + position)
                    )
                    manifests = analyze_publication(directory, root)
                    self.assertEqual(manifests, [manifest_path_for(structured)])
                    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
                    self.assertEqual(manifest["asset"]["format"], "json")
                    self.assertEqual(manifest["reference"]["semantic_model"], model)
                    self.assertEqual(manifest["reference"]["natural_units"], units)
                    self.assertEqual(
                        [experiment["method"] for experiment in manifest["experiments"]],
                        methods,
                    )
                    self.assertEqual(manifest["recommendation"]["method"], methods[0])
                    if model == "lexical":
                        self.assertGreater(manifest["structure"]["references"], 0)
                        self.assertGreater(manifest["structure"]["relations"], 0)
                    self.assertNotRegex(
                        json.dumps(manifest, ensure_ascii=False),
                        r"In the beginning|lexical definition|Blessed is the man",
                    )
                    for experiment in manifest["experiments"]:
                        self.assertEqual(experiment["status"], "passed")
                        self.assertEqual(experiment["metrics"]["lost_units"], 0)
                        self.assertEqual(experiment["metrics"]["fragmented_units"], 0)
                        self.assertGreater(experiment["efficiency"]["characters_per_chunk"], 0)

    def test_semantic_proof_rejects_loss_reorder_fragmentation_and_fusion(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, structured, _item_value = _materialize_structured(root, "lexical")
            report = inspect_asset(structured)
            model = report["_model"]
            units = model["semantic"]["units"]
            cases = {
                "loss": [[units[0]]],
                "reorder": [[units[1]], [units[0]]],
                "fragmentation": [[{**units[0], "payload_sha256": "0" * 64}], [units[1]]],
                "fusion": [[units[0], units[1]]],
            }
            for diagnostic, groups in cases.items():
                with self.subTest(diagnostic=diagnostic):
                    result = _measure_semantic_experiment("lexical-entry", groups, model)
                    self.assertEqual(result["status"], "rejected")
            self.assertIn(
                "semantic-unit-fragmentation",
                _measure_semantic_experiment(
                    "lexical-entry", cases["fragmentation"], model
                )["diagnostics"],
            )
            self.assertIn(
                "semantic-unit-fusion",
                _measure_semantic_experiment("lexical-entry", cases["fusion"], model)[
                    "diagnostics"
                ],
            )

    def test_structured_only_publication_is_indexed_and_transactionally_complete(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, structured, item = _materialize_structured(root, "scripture")
            analyze_publication(directory, root)
            config = _config(root)
            target = root / "index.json"
            publication_index.update_global_index(root, target, config)
            entry = json.loads(target.read_text(encoding="utf-8"))["publications"][0]
            self.assertEqual(entry["assets"], [])
            self.assertEqual(entry["structured"]["model"], "scripture")
            self.assertEqual(entry["structured"]["semantic"]["natural_units"], 4)
            self.assertEqual(
                entry["structured"]["chunking_manifest"],
                manifest_path_for(structured).relative_to(root).as_posix(),
            )
            serialized = json.dumps(entry["structured"], ensure_ascii=False)
            self.assertNotIn("content", serialized)
            allowed = validate_complete_publication(
                item,
                root,
                REPOSITORY_ROOT,
            )
            self.assertIn(manifest_path_for(structured).relative_to(REPOSITORY_ROOT), allowed)

    def test_generic_json_is_not_discovered_or_parsed_as_plain_text(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            root.mkdir(parents=True)
            generic = root / "generic.json"
            generic.write_text('{"text":"prosa genérica"}', encoding="utf-8")
            with self.assertRaises(ContractError):
                inspect_asset(generic)
            with self.assertRaisesRegex(AnalysisError, "sem ativos analisáveis"):
                analyze_scope(root, root)

    def test_global_analysis_commits_each_publication_and_resumes_without_rework(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            subprocess.run(["git", "init", "-b", "dev"], cwd=repository, check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.name", "Fixture"],
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "fixture@example.test"],
                cwd=repository,
                check=True,
            )
            (repository / ".gitignore").write_text(
                "/constructor/.state/\n",
                encoding="utf-8",
            )
            source_root = repository / "src" / "publications"
            _materialize(source_root, _item("42", "Primeira"))
            _materialize(source_root, _item("43", "Segunda"))
            catalog = repository / "config" / "publication-chunking-methods.json"
            catalog.parent.mkdir(parents=True)
            catalog.write_bytes(
                (REPOSITORY_ROOT / "config" / "publication-chunking-methods.json").read_bytes()
            )
            subprocess.run(
                ["git", "add", "--", ".gitignore", "config", "src"],
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Base"],
                cwd=repository,
                check=True,
                capture_output=True,
            )
            config = _config(source_root)
            config["source_root"] = "src/publications"
            config["runtime_state_root"] = "constructor/.state/egwsearch"
            config["intelligence"]["index_path"] = "src/publications/index.json"

            with (
                patch("publication_analysis.REPOSITORY_ROOT", repository),
                patch("publication_analysis.CATALOG_PATH", catalog),
                patch("publication_index.REPOSITORY_ROOT", repository),
            ):
                manifests, commits = analyze_and_commit_scope(
                    source_root,
                    source_root,
                    config,
                )
                repeated, repeated_commits = analyze_and_commit_scope(
                    source_root,
                    source_root,
                    config,
                )

            self.assertEqual(len(manifests), 4)
            self.assertEqual(len(commits), 2)
            self.assertEqual(repeated, [])
            self.assertEqual(repeated_commits, [])
            for commit in commits:
                changed = subprocess.run(
                    ["git", "show", "--pretty=format:", "--name-only", commit],
                    cwd=repository,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.splitlines()
                publication_roots = {
                    "/".join(path.split("/")[:-1])
                    for path in changed
                    if path.endswith(".chunking.json")
                }
                self.assertEqual(len(publication_roots), 1)
                self.assertIn("src/publications/index.json", changed)
                self.assertIn("src/publications/chunking-learning.json", changed)
            self.assertEqual(
                subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repository,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout,
                "",
            )

    def test_fresh_success_skips_for_24_hours_and_force_recalculates(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, _epub, _pdf = _materialize(root, _item())
            started = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
            manifests = analyze_publication(directory, root, now=started)
            before = {path: path.stat().st_mtime_ns for path in manifests}
            learning_before = learning_path_for(root).stat().st_mtime_ns

            with patch("publication_analysis.inspect_asset") as inspector:
                analyze_publication(
                    directory,
                    root,
                    now=started + timedelta(hours=23, minutes=59),
                )
            inspector.assert_not_called()
            self.assertEqual(before, {path: path.stat().st_mtime_ns for path in manifests})
            self.assertEqual(learning_before, learning_path_for(root).stat().st_mtime_ns)

            forced_at = started + timedelta(hours=1)
            with patch(
                "publication_analysis.inspect_asset",
                wraps=inspect_asset,
            ) as inspector:
                analyze_publication(
                    directory,
                    root,
                    now=forced_at,
                    force_recalculate=True,
                )
            self.assertEqual(inspector.call_count, 2)
            refreshed = json.loads(manifests[0].read_text(encoding="utf-8"))
            self.assertEqual(refreshed["execution"]["status"], "completed")
            self.assertEqual(refreshed["execution"]["completed_at"], "2026-08-02T13:00:00Z")

    def test_expired_or_failed_proof_recalculates(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, epub, _pdf = _materialize(root, _item())
            started = datetime(2026, 8, 2, 12, tzinfo=timezone.utc)
            analyze_publication(directory, root, now=started)
            with patch(
                "publication_analysis.inspect_asset",
                wraps=inspect_asset,
            ) as inspector:
                analyze_publication(directory, root, now=started + timedelta(hours=24))
            self.assertEqual(inspector.call_count, 2)

            manifest = manifest_path_for(epub)
            document = json.loads(manifest.read_text(encoding="utf-8"))
            document["execution"]["status"] = "failed"
            write_json_atomic(manifest, document)
            with patch(
                "publication_analysis.inspect_asset",
                wraps=inspect_asset,
            ) as inspector:
                analyze_scope(epub, root, now=started + timedelta(hours=25))
            self.assertEqual(inspector.call_count, 1)

            document = json.loads(manifest.read_text(encoding="utf-8"))
            document["execution"]["completed_at"] = "2026-08-04T12:00:00Z"
            write_json_atomic(manifest, document)
            with patch(
                "publication_analysis.inspect_asset",
                wraps=inspect_asset,
            ) as inspector:
                analyze_scope(epub, root, now=started + timedelta(hours=26))
            self.assertEqual(inspector.call_count, 1)

    def test_force_flag_propagates_through_downloader_and_indexer(self) -> None:
        wrapper = (MODULE_ROOT / "run-baixar.ts").read_text(encoding="utf-8")
        package = json.loads((REPOSITORY_ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertIn("...rawArguments", wrapper)
        self.assertIn("--tool=publication_analysis.py", package["scripts"]["publications:analyze"])
        downloader_arguments = baixar.build_parser().parse_args(["--force-recalculate"])
        self.assertTrue(downloader_arguments.force_recalculate)
        index_arguments = publication_index._parser().parse_args(
            ["--all", "--analyze", "--force-recalculate"]
        )
        self.assertTrue(index_arguments.analyze)
        self.assertTrue(index_arguments.force_recalculate)

        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, _epub, _pdf = _materialize(root, _item())
            config = _config(root)
            target = root / "index.json"
            target.write_text('{"publications": []}', encoding="utf-8")
            with (
                patch.object(publication_index, "load_config", return_value=config),
                patch.object(publication_index, "configured_index_path", return_value=target),
                patch.object(
                    publication_index,
                    "analyze_and_commit_scope",
                    return_value=([], []),
                ) as analysis,
                patch.object(publication_index, "update_global_index", return_value=target),
            ):
                self.assertEqual(
                    publication_index.main(
                        ["--config", "unused.json", "--all", "--analyze", "--force-recalculate"]
                    ),
                    0,
                )
            self.assertTrue(analysis.call_args.kwargs["force_recalculate"])

            reset_arguments = publication_index._parser().parse_args(
                ["--all", "--analyze", "--reset"]
            )
            self.assertTrue(reset_arguments.reset)

            with (
                patch.object(baixar, "analyze_publication", return_value=[]) as analysis,
                patch.object(baixar, "update_global_index", return_value=target),
            ):
                baixar.finalize_publication_intelligence(
                    _item(),
                    root,
                    config,
                    force_recalculate=True,
                )
            self.assertTrue(analysis.call_args.kwargs["force_recalculate"])

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

    def test_duplicate_existing_entry_forces_integral_index_rebuild(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary) / "publications"
            directory, _epub, _pdf = _materialize(root, _item())
            analyze_publication(directory, root)
            config = _config(root)
            target = root / "index.json"
            publication_index.update_global_index(root, target, config)
            document = json.loads(target.read_text(encoding="utf-8"))
            duplicate = json.loads(json.dumps(document["publications"][0]))
            duplicate["id"] = "corrupt:duplicate"
            document["publications"].append(duplicate)
            write_json_atomic(target, document)

            publication_index.update_global_index(
                root,
                target,
                config,
                publication=directory,
            )

            repaired = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(len(repaired["publications"]), 1)

    def test_index_manifest_is_agnostic_to_index_state_and_quantity(self) -> None:
        self.assertEqual(
            json.loads(
                (REPOSITORY_ROOT / "src" / "publications" / "index.manifest.json").read_text(
                    encoding="utf-8"
                )
            ),
            publication_index.INDEX_MANIFEST,
        )
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
