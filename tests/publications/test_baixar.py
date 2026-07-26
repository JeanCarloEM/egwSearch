# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Testes sem rede do downloader canônico."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "src" / "publications" / "egw"
sys.path.insert(0, str(CONTRACT_ROOT))

import baixar  # noqa: E402
from publication_contract import hash_file, publication_identity  # noqa: E402


class _Progress:
    def update(self, _size: int) -> None:
        return None

    def close(self) -> None:
        return None


class DownloaderTests(unittest.TestCase):
    def test_private_dns_is_blocked(self) -> None:
        with patch.object(
            baixar.socket,
            "getaddrinfo",
            return_value=[(None, None, None, None, ("127.0.0.1", 443))],
        ):
            with self.assertRaises(baixar.DownloadError):
                baixar._validate_public_dns("media2.egwwritings.org")

    def test_asset_install_is_atomic_and_repetition_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary)
            identity = publication_identity("egw", "pt-br", "livros", "Atos")

            def fake_stream(*_args, **_kwargs):
                destination = source_root / identity.relative_directory()
                destination.mkdir(parents=True, exist_ok=True)
                partial = destination / ".fixture.pdf.partial"
                partial.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
                hashes = hash_file(partial)
                return (
                    partial,
                    {**hashes.as_dict(), "size": hashes.size},
                    "https://media2.egwwritings.org/pdf/pt_AA.pdf",
                    "pdf",
                )

            with patch.object(baixar, "_stream_to_temporary", side_effect=fake_stream):
                target, record, installed = baixar.download_asset(
                    object(),
                    "https://media2.egwwritings.org/pdf/pt_AA.pdf",
                    identity,
                    source_root,
                    {},
                    lambda **_kwargs: _Progress(),
                )
                self.assertTrue(installed)
                self.assertTrue(target.is_file())
                self.assertEqual(record["hashes"]["sha256"], hash_file(target).sha256)

                repeated_target, _record, repeated_installed = baixar.download_asset(
                    object(),
                    "https://media2.egwwritings.org/pdf/pt_AA.pdf",
                    identity,
                    source_root,
                    {},
                    lambda **_kwargs: _Progress(),
                )
                self.assertEqual(repeated_target, target)
                self.assertFalse(repeated_installed)


if __name__ == "__main__":
    unittest.main()
