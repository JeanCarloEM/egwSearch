# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Testes da apresentação compartilhada sem depender de terminal real."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
import sys
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(MODULE_ROOT))

from publication_console import PublicationReporter, compact_path  # noqa: E402


class PublicationConsoleTests(unittest.TestCase):
    def test_long_path_is_truncated_predictably_with_basename(self) -> None:
        value = "src/publications/" + "segmento-muito-longo/" * 8 + "livro.epub"
        compact = compact_path(value, 42)
        self.assertLessEqual(len(compact), 42)
        self.assertIn("…", compact)
        self.assertTrue(compact.endswith("livro.epub"))

    def test_non_terminal_output_has_no_ansi_and_preserves_metrics(self) -> None:
        stream = StringIO()
        reporter = PublicationReporter(
            "Laboratório",
            stream=stream,
            force_terminal=False,
        )
        reporter.start("src/publications/exemplo/livro.pdf")
        reporter.experiments(
            "src/publications/exemplo/livro.pdf",
            [
                {
                    "method": "paragraph",
                    "status": "passed",
                    "chunk_count": 12,
                    "_duration_ms": 3,
                    "efficiency": {"characters_per_chunk": 480},
                    "metrics": {"accuracy_ppm": 1_000_000, "error_ppm": 0},
                    "diagnostics": [],
                }
            ],
        )
        output = stream.getvalue()
        self.assertNotIn("\x1b[", output)
        self.assertIn("paragraph", output)
        self.assertIn("100.0%", output)
        self.assertIn("0.0%", output)

    def test_embedded_reporter_does_not_repeat_parent_header(self) -> None:
        stream = StringIO()
        parent = PublicationReporter("Downloader", stream=stream, force_terminal=False)
        child = parent.child("Indexador")
        child.start("índice")
        self.assertEqual(stream.getvalue(), "")
        child.result("Indexação", {"publicações": 1})
        self.assertIn("Indexação", stream.getvalue())

    def test_compact_mode_keeps_one_distinct_line_per_resource(self) -> None:
        stream = StringIO()
        reporter = PublicationReporter(
            "Global",
            stream=stream,
            force_terminal=False,
            compact=True,
        )
        row = {
            "method": "paragraph",
            "status": "passed",
            "chunk_count": 4,
            "metrics": {"accuracy_ppm": 990_000, "error_ppm": 10_000},
        }
        reporter.experiments("um/caminho/muito/longo/recurso-a.pdf", [row])
        reporter.experiments("um/caminho/muito/longo/recurso-b.epub", [row])
        lines = [line for line in stream.getvalue().splitlines() if line]
        self.assertEqual(len(lines), 2)
        self.assertIn("recurso-a.pdf", lines[0])
        self.assertIn("recurso-b.epub", lines[1])
        self.assertTrue(all(len(line) <= reporter.width for line in lines))


if __name__ == "__main__":
    unittest.main()
