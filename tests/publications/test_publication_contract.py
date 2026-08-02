# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Testes sem rede do contrato compartilhado de publicacoes."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(CONTRACT_ROOT))

from publication_contract import (  # noqa: E402
    ContractError,
    build_asset_identity_index,
    build_source_document,
    choose_variant_path,
    hash_file,
    publication_identity,
    read_source_records,
    title_acronym,
    uri_slug,
    validate_unique_asset_sha512,
    validate_file_signature,
    write_json_atomic,
)
import publication_contract  # noqa: E402


class PublicationContractTests(unittest.TestCase):
    def test_title_and_path_preserve_editorial_content(self) -> None:
        identity = publication_identity(
            "egw",
            "pt-br",
            "livros",
            "  Atos   Dos Apóstolos (nova edição) ",
        )
        self.assertEqual(identity.title, "Atos Dos Apóstolos (nova edição)")
        self.assertEqual(identity.acronym, "adane")
        self.assertEqual(
            identity.route_slug,
            "atos-dos-apostolos-nova-edicao",
        )
        self.assertEqual(
            identity.relative_directory().as_posix(),
            "geral/egw/pt-br/livros/atos-dos-apostolos-nova-edicao",
        )
        categorized = publication_identity(
            "egw", "pt-br", "comentarios", "Daniel", category="Comentários Bíblicos"
        )
        self.assertEqual(categorized.category, "comentarios-biblicos")
        self.assertEqual(
            categorized.relative_directory().as_posix(),
            "comentarios-biblicos/egw/pt-br/comentarios/daniel",
        )
        egw = publication_identity("egw", "en", "books", "Education", category="egw")
        self.assertEqual(egw.relative_directory().as_posix(), "egw/en/books/education")
        self.assertEqual(uri_slug('A: B/C?'), "a-bc")

    def test_uri_slug_is_ascii_rfc3986_and_portable(self) -> None:
        self.assertEqual(
            uri_slug("A Maravilhosa Graça de Deus"),
            "a-maravilhosa-graca-de-deus",
        )
        self.assertEqual(uri_slug("Christ’s Object Lessons"), "christs-object-lessons")
        self.assertEqual(uri_slug("Æsop, Œuvre & Straße"), "aesop-oeuvre-strasse")
        self.assertEqual(uri_slug("CON"), "u-con")
        self.assertRegex(uri_slug("東京"), r"^u-[0-9a-f]{12}$")
        self.assertLessEqual(len(uri_slug("Título " * 100).encode("ascii")), 180)

    def test_redundant_inverted_article_is_removed_only_when_identical(self) -> None:
        identity = publication_identity(
            "egw", "pt-br", "livros", "A CIÊNCIA DO BOM VIVER, A", category="egw"
        )
        self.assertEqual(identity.title, "A CIÊNCIA DO BOM VIVER")
        self.assertEqual(identity.route_slug, "a-ciencia-do-bom-viver")
        self.assertEqual(identity.acronym, "acdbv")
        self.assertEqual(uri_slug("Ciência do Bom Viver, A"), "ciencia-do-bom-viver-a")
        self.assertEqual(
            uri_slug("A Ciência do Bom Viver, O"), "a-ciencia-do-bom-viver-o"
        )

    def test_single_word_and_unicode_fallback_acronyms(self) -> None:
        self.assertEqual(title_acronym("Maranatha"), "maranatha")
        self.assertRegex(title_acronym("東京"), r"^u[0-9a-f]{12}$")

    def test_hashes_signatures_and_variants(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pdf = root / "book.pdf"
            pdf.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
            hashes = hash_file(pdf, chunk_size=3)
            self.assertEqual(hashes.size, pdf.stat().st_size)
            self.assertEqual(len(hashes.sha1), 40)
            self.assertEqual(len(hashes.sha256), 64)
            self.assertEqual(len(hashes.sha512), 128)
            validate_file_signature(pdf, "pdf")
            selected, duplicate = choose_variant_path(pdf, hashes.sha256)
            self.assertEqual(selected, pdf)
            self.assertTrue(duplicate)

            other = root / "other.pdf"
            other.write_bytes(b"%PDF-1.7\nother\n%%EOF")
            other_hash = hash_file(other).sha256
            selected, duplicate = choose_variant_path(pdf, other_hash)
            self.assertFalse(duplicate)
            self.assertEqual(selected.name, f"book.{other_hash[:8]}.pdf")

            epub = root / "book.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr(
                    "mimetype",
                    b"application/epub+zip",
                    compress_type=zipfile.ZIP_STORED,
                )
            validate_file_signature(epub, "epub")

    def test_sha512_duplicate_cannot_span_publication_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "canonical" / "book.pdf"
            second = root / "wrong-name" / "other.pdf"
            first.parent.mkdir()
            second.parent.mkdir()
            payload = b"%PDF-1.7\nidentical\n%%EOF"
            first.write_bytes(payload)
            second.write_bytes(payload)
            hashes = hash_file(first)
            metadata = {
                "https://example.test/book.pdf": {"sha256": hashes.sha256}
            }
            for directory in (first.parent, second.parent):
                (directory / "book.source.json").write_text(
                    json.dumps(metadata), encoding="utf-8"
                )
            index = build_asset_identity_index(root)
            with self.assertRaisesRegex(ContractError, "duplicacao global SHA-512"):
                validate_unique_asset_sha512(index)
            second.write_bytes(b"%PDF-1.7\ndifferent\n%%EOF")
            validate_unique_asset_sha512(build_asset_identity_index(root))

    def test_invalid_signature_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "invalid.pdf"
            candidate.write_bytes(b"not-pdf")
            with self.assertRaises(ContractError):
                validate_file_signature(candidate, "pdf")

    def test_legacy_metadata_and_closed_v2_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            metadata = Path(temporary) / "Book.source.json"
            metadata.write_text(
                json.dumps(
                    {
                        "https://media2.egwwritings.org/pdf/pt_AA.pdf": {
                            "acesso": 1746942924,
                            "sha256": "a" * 64,
                        }
                    }
                ),
                encoding="utf-8",
            )
            records = read_source_records(metadata)
            self.assertEqual(records[0]["format"], "pdf")
            identity = publication_identity("egw", "pt-br", "livros", "Atos")
            records[0]["size"] = 10
            records[0]["hashes"] = {
                "sha1": "b" * 40,
                "sha256": "a" * 64,
                "sha512": "c" * 128,
            }
            document = build_source_document(identity, records)
            self.assertEqual(
                set(document),
                {"schema_version", "identity", "sources"},
            )
            self.assertEqual(document["schema_version"], "egw-source/v2")
            self.assertEqual(document["identity"]["tags"], [])

    def test_atomic_json_retries_transient_permission_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "state.json"
            original_replace = publication_contract.os.replace
            calls = 0

            def transient_replace(source: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls < 3:
                    raise PermissionError("fixture: arquivo temporariamente bloqueado")
                original_replace(source, destination)

            with mock.patch.object(
                publication_contract.os,
                "replace",
                side_effect=transient_replace,
            ):
                write_json_atomic(target, {"status": "ok"})

            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"status": "ok"})
            self.assertEqual(calls, 3)


if __name__ == "__main__":
    unittest.main()
