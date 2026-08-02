# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Testes rápidos da seleção editorial de capas locais."""

from __future__ import annotations

from pathlib import Path
import struct
import sys
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(MODULE_ROOT))

from publication_covers import CoverError, _pdf_cover_bytes  # noqa: E402


class PublicationCoverTests(unittest.TestCase):
    def test_pdf_selects_title_page_instead_of_technical_first_page(self) -> None:
        source = (
            REPOSITORY_ROOT
            / "src/publications/egw/en/books/the-impending-conflict/tic.pdf"
        )
        payload = _pdf_cover_bytes(source, "The Impending Conflict", "Ellen G. White")

        self.assertTrue(payload.startswith(b"\x89PNG\r\n\x1a\n"))
        width, height = struct.unpack(">II", payload[16:24])
        self.assertLessEqual(max(width, height), 800)
        self.assertGreater(width, 300)
        self.assertGreater(height, width)

    def test_pdf_rejects_page_without_matching_editorial_title(self) -> None:
        source = (
            REPOSITORY_ROOT
            / "src/publications/egw/en/books/the-impending-conflict/tic.pdf"
        )
        with self.assertRaises(CoverError):
            _pdf_cover_bytes(source, "Título inexistente e incompatível", "Autor ausente")


if __name__ == "__main__":
    unittest.main()
