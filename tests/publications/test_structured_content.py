# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(MODULE_ROOT))

from acquisition import CatalogItem, CatalogSegment  # noqa: E402
from structured_content import (  # noqa: E402
    StructuredContentError,
    build_structured_document,
    validate_structured_artifact,
    write_structured_artifact,
)


def _item(model: str, segments: list[str], *, title: str = "Fixture") -> CatalogItem:
    return CatalogItem(
        remote_id="42",
        collection_id="fixture",
        collection_name="Fixture",
        author_name="Source tradition",
        author_key="source-tradition",
        language_original="en",
        language="en",
        language_path="en",
        publication_type="bible" if model == "scripture" else model,
        title_original=title,
        title_normalized=title,
        public_url="https://example.test/book/b42",
        category_name="Bible",
        category_path="biblia",
        segments=tuple(
            CatalogSegment(
                remote_id=str(index),
                url=f"https://example.test/read/{index}",
                order=index,
                title=f"Unit {index}",
                html=html,
            )
            for index, html in enumerate(segments, 1)
        ),
        content_model=model,
        content_options={"collection": "BODY", "script": "Latn"},
    )


class ScriptureCorpusTests(unittest.TestCase):
    def test_isolates_verses_across_genres_and_preserves_marks(self) -> None:
        item = _item(
            "scripture",
            [
                '<p data-book="Genesis" data-chapter="1" data-verse="1">In the <em>beginning</em>.</p>',
                '<p data-book="Psalms" data-chapter="1" data-verse="1" align="center"><strong>Blessed</strong> is the man.</p>',
                '<p data-book="Isaiah" data-chapter="1" data-verse="1">The vision.</p>',
                '<p data-book="Romans" data-chapter="1" data-verse="1">Paul, a servant.</p>',
            ],
            title="Verified Version",
        )
        document = build_structured_document(item)
        version = next(iter(document["text"].values()))["BODY"]
        self.assertEqual(version["GEN"]["1"]["1"]["content"][1], {
            "text": "beginning",
            "marks": ["italic"],
        })
        self.assertEqual(set(version), {"GEN", "PSA", "ISA", "ROM"})
        self.assertEqual(document["proof"]["counts"]["verses"], 4)
        self.assertEqual(len(document["proof"]["source"]["segments"]), 4)

    def test_implicit_reference_keeps_inline_emphasis(self) -> None:
        document = build_structured_document(
            _item("scripture", ["<p>Genesis 1:1 In the <em>beginning</em>.</p>"])
        )
        verse = next(iter(document["text"].values()))["BODY"]["GEN"]["1"]["1"]
        self.assertEqual("".join(run["text"] for run in verse["content"]), "In the beginning.")
        self.assertIn("italic", verse["content"][1]["marks"])

    def test_rejects_duplicate_gap_concatentation_and_residual(self) -> None:
        cases = [
            [
                '<p data-book="Genesis" data-chapter="1" data-verse="1">A</p>',
                '<p data-book="Genesis" data-chapter="1" data-verse="1">B</p>',
            ],
            [
                '<p data-book="Genesis" data-chapter="1" data-verse="1">A</p>',
                '<p data-book="Genesis" data-chapter="1" data-verse="3">C</p>',
            ],
            ["<p>Genesis 1:1 A Genesis 1:2 B</p>"],
            ["<p>Genesis 1:1 A</p><p>foreign payload</p>"],
        ]
        for segments in cases:
            with self.subTest(segments=segments):
                with self.assertRaises(StructuredContentError):
                    build_structured_document(_item("scripture", segments))

    def test_title_does_not_override_observed_lexical_structure(self) -> None:
        with self.assertRaisesRegex(StructuredContentError, "sem versículos"):
            build_structured_document(
                _item(
                    "scripture",
                    ["<h4>(1) α, alpha</h4><p>A lexical definition.</p>"],
                    title="Holy Bible",
                )
            )

    def test_writes_deterministic_utf8_without_bom_or_crlf(self) -> None:
        item = _item(
            "scripture",
            ['<p data-book="Genesis" data-chapter="1" data-verse="1">Princípio.</p>'],
        )
        with tempfile.TemporaryDirectory() as temporary:
            path, evidence = write_structured_artifact(Path(temporary), item)
            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertNotIn(b"\r\n", raw)
            self.assertEqual(evidence["encoding"], "utf-8")
            self.assertEqual(validate_structured_artifact(path), json.loads(raw.decode("utf-8")))

    def test_rejects_tampered_hash_and_duplicate_json_key(self) -> None:
        item = _item(
            "scripture",
            ['<p data-book="Genesis" data-chapter="1" data-verse="1">A.</p>'],
        )
        with tempfile.TemporaryDirectory() as temporary:
            path, _evidence = write_structured_artifact(Path(temporary), item)
            document = json.loads(path.read_text(encoding="utf-8"))
            version = next(iter(document["text"].values()))
            version["BODY"]["GEN"]["1"]["1"]["content"][0]["text"] = "B."
            path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(StructuredContentError, "hash interno"):
                validate_structured_artifact(path)
            path.write_text(
                '{"schema":"scripture-corpus/v1","schema":"scripture-corpus/v1"}',
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(StructuredContentError, "chave JSON duplicada"):
                validate_structured_artifact(path)


class LexicalAndConcordanceTests(unittest.TestCase):
    def test_generic_dictionary_heading_receives_stable_source_key(self) -> None:
        item = _item(
            "lexical",
            ["<h4>Abba</h4><p>A Semitic word for father.</p>"],
        )
        item.content_options["heading_entries"] = True
        document = build_structured_document(item)
        self.assertEqual(list(document["entries"]), ["1:1"])
        self.assertEqual(document["entries"]["1:1"]["lemma"], "Abba")

    def test_lexicon_separates_original_from_translation(self) -> None:
        document = build_structured_document(
            _item(
                "lexical",
                [
                    '<h4 data-entry-id="G1" data-lemma="α" data-romanization="alpha">(1) α, alpha</h4>'
                    '<p>The first letter of the Greek alphabet.</p>'
                    '<p>Genesis 1:1</p>'
                ],
            )
        )
        entry = document["entries"]["G1"]
        self.assertEqual(entry["definitions"]["en"], ["The first letter of the Greek alphabet."])
        self.assertEqual(entry["translations"], {})
        self.assertEqual(entry["references"][0]["book"], "GEN")

    def test_concordance_requires_and_isolates_references(self) -> None:
        document = build_structured_document(
            _item(
                "concordance",
                ["<h4>(1) α, alpha</h4><p>α Matthew 1:1; Romans 1:1.</p>"],
            )
        )
        self.assertEqual(
            [(ref["book"], ref["chapter"], ref["verse"]) for ref in document["entries"]["1"]["references"]],
            [("MAT", "1", "1"), ("ROM", "1", "1")],
        )
        self.assertEqual(document["entries"]["1"]["relations"][0]["form"], "α")
        with self.assertRaises(StructuredContentError):
            build_structured_document(
                _item("concordance", ["<h4>(1) α, alpha</h4><p>No reference.</p>"])
            )


if __name__ == "__main__":
    unittest.main()
