# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Testes sem rede do downloader canônico."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(CONTRACT_ROOT))

import baixar  # noqa: E402
from acquisition import CatalogAsset, CatalogItem, build_source_v3  # noqa: E402
from publication_contract import (  # noqa: E402
    hash_file,
    publication_identity,
    write_json_atomic,
)


class _Progress:
    def update(self, _size: int) -> None:
        return None

    def close(self) -> None:
        return None


class _Response:
    def __init__(self, status: int, headers: dict | None = None) -> None:
        self.status_code = status
        self.headers = headers or {}
        self.closed = False

    def close(self) -> None:
        self.closed = True


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

            with patch.object(
                baixar,
                "_stream_to_temporary",
                side_effect=fake_stream,
            ) as stream_mock:
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
                baixar.update_metadata(source_root, identity, [record])

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
                self.assertEqual(stream_mock.call_count, 1)

    def test_incomplete_file_is_not_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary)
            identity = publication_identity("egw", "pt-br", "livros", "Atos")
            directory = source_root / identity.relative_directory()
            directory.mkdir(parents=True)
            partial = directory / ".download-fixture.pdf.partial"
            partial.write_bytes(b"%PDF-1.7\npartial")
            self.assertIsNone(
                baixar.preflight_existing_asset(
                    "https://media2.egwwritings.org/pdf/pt_AA.pdf",
                    identity,
                    source_root,
                )
            )

    def test_different_content_is_preserved_as_variant(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary)
            identity = publication_identity("egw", "pt-br", "livros", "Atos")
            directory = source_root / identity.relative_directory()
            directory.mkdir(parents=True)
            original = directory / identity.asset_name("pdf")
            original.write_bytes(b"%PDF-1.7\noriginal\n%%EOF")

            def fake_stream(*_args, **_kwargs):
                partial = directory / ".fixture.pdf.partial"
                partial.write_bytes(b"%PDF-1.7\nupdated\n%%EOF")
                hashes = hash_file(partial)
                return (
                    partial,
                    {**hashes.as_dict(), "size": hashes.size},
                    "https://media2.egwwritings.org/pdf/pt_AA.pdf",
                    "pdf",
                )

            with patch.object(baixar, "_stream_to_temporary", side_effect=fake_stream):
                target, _record, installed = baixar.download_asset(
                    object(),
                    "https://media2.egwwritings.org/pdf/pt_AA.pdf",
                    identity,
                    source_root,
                    {},
                    lambda **_kwargs: _Progress(),
                )
            self.assertTrue(installed)
            self.assertNotEqual(target, original)
            self.assertEqual(original.read_bytes(), b"%PDF-1.7\noriginal\n%%EOF")

    def test_429_respects_retry_after(self) -> None:
        session = Mock()
        session.get.side_effect = [
            _Response(429, {"retry-after": "7"}),
            _Response(200),
        ]
        limiter = Mock()
        response = baixar._get_with_retry(
            session,
            "https://media2.egwwritings.org/pdf/test.pdf",
            {
                "connect_timeout_seconds": 1,
                "read_timeout_seconds": 1,
                "max_attempts": 3,
            },
            limiter=limiter,
        )
        self.assertEqual(response.status_code, 200)
        limiter.backoff.assert_called_once_with(1, "7")
        self.assertEqual(session.get.call_count, 2)

    def test_403_stops_without_retry(self) -> None:
        session = Mock()
        session.get.return_value = _Response(403)
        limiter = Mock()
        with self.assertRaises(baixar.OriginBlocked):
            baixar._get_with_retry(
                session,
                "https://media2.egwwritings.org/pdf/test.pdf",
                {
                    "connect_timeout_seconds": 1,
                    "read_timeout_seconds": 1,
                    "max_attempts": 3,
                },
                limiter=limiter,
            )
        self.assertEqual(session.get.call_count, 1)
        limiter.backoff.assert_not_called()

    def test_remote_hash_change_invalidates_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary)
            identity = publication_identity("autor", "en", "books", "Title")
            directory = source_root / identity.relative_directory()
            directory.mkdir(parents=True)
            target = directory / identity.asset_name("pdf")
            target.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
            hashes = hash_file(target)
            item = CatalogItem(
                remote_id="1",
                collection_id="en-pioneers",
                collection_name="Adventist Pioneer Library",
                author_name="Author",
                author_key="autor",
                language_original="en",
                language="en",
                language_path="en",
                publication_type="books",
                title_original="Title",
                title_normalized="Title",
                public_url="https://text.egwwritings.org/book/b1",
            )
            url = "https://media2.egwwritings.org/pdf/en_Title.pdf"
            document = build_source_v3(
                item,
                "completed",
                [
                    {
                        "format": "pdf",
                        "url": url,
                        "size": hashes.size,
                        "hashes": hashes.as_dict(),
                    }
                ],
            )
            write_json_atomic(directory / identity.metadata_name(), document)
            self.assertIsNotNone(
                baixar.preflight_existing_asset(url, identity, source_root)
            )
            self.assertIsNone(
                baixar.preflight_existing_asset(
                    url,
                    identity,
                    source_root,
                    CatalogAsset("pdf", url, remote_hash="f" * 64),
                )
            )

    def test_conditional_revalidation_uses_etag_and_keeps_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary)
            identity = publication_identity("autor", "en", "books", "Title")
            directory = source_root / identity.relative_directory()
            directory.mkdir(parents=True)
            target = directory / identity.asset_name("pdf")
            target.write_bytes(b"%PDF-1.7\nfixture\n%%EOF")
            before = target.stat().st_mtime_ns
            hashes = hash_file(target)
            item = CatalogItem(
                remote_id="1",
                collection_id="en-pioneers",
                collection_name="Adventist Pioneer Library",
                author_name="Author",
                author_key="autor",
                language_original="en",
                language="en",
                language_path="en",
                publication_type="books",
                title_original="Title",
                title_normalized="Title",
                public_url="https://text.egwwritings.org/book/b1",
            )
            url = "https://media2.egwwritings.org/pdf/en_Title.pdf"
            document = build_source_v3(
                item,
                "completed",
                [
                    {
                        "format": "pdf",
                        "url": url,
                        "etag": "\"fixture\"",
                        "last_modified": "Sun, 26 Jul 2026 00:00:00 GMT",
                        "size": hashes.size,
                        "hashes": hashes.as_dict(),
                    }
                ],
            )
            write_json_atomic(directory / identity.metadata_name(), document)

            def not_modified(*args, **_kwargs):
                config = args[3]
                self.assertEqual(
                    config["_conditional_headers"],
                    {
                        "If-None-Match": "\"fixture\"",
                        "If-Modified-Since": "Sun, 26 Jul 2026 00:00:00 GMT",
                    },
                )
                raise baixar.NotModified()

            with patch.object(
                baixar,
                "_stream_to_temporary",
                side_effect=not_modified,
            ):
                repeated, _record, installed = baixar.download_asset(
                    object(),
                    url,
                    identity,
                    source_root,
                    {
                        "connect_timeout_seconds": 1,
                        "read_timeout_seconds": 1,
                    },
                    lambda **_kwargs: _Progress(),
                    revalidate=True,
                )
            self.assertEqual(repeated, target)
            self.assertFalse(installed)
            self.assertEqual(target.stat().st_mtime_ns, before)


if __name__ == "__main__":
    unittest.main()
