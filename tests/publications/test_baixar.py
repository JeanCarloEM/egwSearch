# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Testes sem rede do downloader canônico."""

from __future__ import annotations

import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(CONTRACT_ROOT))

import baixar  # noqa: E402
from acquisition import CatalogAsset, CatalogItem, CatalogSegment, build_source_v3  # noqa: E402
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


class _FakeOptions:
    def __init__(self) -> None:
        self.arguments: list[str] = []

    def add_argument(self, value: str) -> None:
        self.arguments.append(value)


class _FakeSwitch:
    def __init__(self, driver) -> None:
        self.driver = driver

    def window(self, handle: str) -> None:
        self.driver.current_handle = handle


class _FakeDriver:
    def __init__(self, page_sources: list[str] | None = None) -> None:
        self.window_handles = ["main"]
        self.current_handle = "main"
        self.switch_to = _FakeSwitch(self)
        self.page_sources = page_sources or ["<html><div class='book-list-item'></div></html>"]
        self.visited: list[str] = []
        self.quit_count = 0
        self.title = "Catalogo"
        self.current_url = "https://egwwritings.org/allCollection/pt/245"

    @property
    def page_source(self) -> str:
        if len(self.page_sources) > 1:
            return self.page_sources.pop(0)
        return self.page_sources[0]

    def set_window_size(self, _width: int, _height: int) -> None:
        return None

    def get(self, url: str) -> None:
        self.visited.append(url)
        self.current_url = url

    def execute_script(self, _script: str) -> int:
        return 100

    def find_elements(self, by, value):
        if value == "book-list-item":
            return [object()]
        return []

    def quit(self) -> None:
        self.quit_count += 1


class _FakeProcess:
    def __init__(self) -> None:
        self.returncode = None
        self.poll_count = 0

    def poll(self):
        self.poll_count += 1
        if self.poll_count >= 2:
            self.returncode = 0
        return self.returncode


class _FakeActionChains:
    def __init__(self, _driver) -> None:
        pass

    def move_to_element(self, _element):
        return self

    def click(self):
        return self

    def perform(self) -> None:
        return None


class _FakeWait:
    def __init__(self, driver, _timeout, poll_frequency=0.5) -> None:
        self.driver = driver
        self.poll_frequency = poll_frequency

    def until(self, predicate):
        return predicate(self.driver)


class _FakeEC:
    @staticmethod
    def presence_of_element_located(_locator):
        return lambda _driver: object()


class _FakeBy:
    CSS_SELECTOR = "css selector"
    CLASS_NAME = "class name"
    TAG_NAME = "tag name"


class _FakePsutil:
    Error = RuntimeError

    @staticmethod
    def process_iter(_attributes):
        return []


def _runtime(driver_factory):
    return {
        "psutil": _FakePsutil,
        "requests": Mock(Session=Mock(return_value=Mock(headers={}, close=Mock()))),
        "tqdm": lambda **_kwargs: _Progress(),
        "webdriver": Mock(Firefox=driver_factory),
        "ActionChains": _FakeActionChains,
        "By": _FakeBy,
        "FirefoxOptions": _FakeOptions,
        "EC": _FakeEC,
        "WebDriverWait": _FakeWait,
    }


class DownloaderTests(unittest.TestCase):
    @staticmethod
    def _runtime_paths(root: Path) -> dict[str, Path]:
        return {
            "root": root,
            "browser_profile": root / "profiles" / "egwwritings",
        }

    def test_private_dns_is_blocked(self) -> None:
        with patch.object(
            baixar.socket,
            "getaddrinfo",
            return_value=[(None, None, None, None, ("127.0.0.1", 443))],
        ):
            with self.assertRaises(baixar.DownloadError):
                baixar._validate_public_dns("media2.egwwritings.org")

    def test_fixture_output_is_always_segregated_from_canonical_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = root / "src" / "publications"
            runtime = root / "constructor" / ".state" / "egwsearch"
            resolved = baixar._fixture_source_root(canonical, runtime, None)
            self.assertEqual(resolved, (runtime / "tmp" / "fixture-output").resolve())
            with self.assertRaises(baixar.ContractError):
                baixar._fixture_source_root(canonical, runtime, canonical)
            with self.assertRaises(baixar.ContractError):
                baixar._fixture_source_root(canonical, runtime, root)

    def test_lightweight_public_projection_preserves_path_and_book_id(self) -> None:
        projected = baixar._lightweight_public_url(
            "https://egwwritings.org/book/b14389"
        )
        self.assertEqual(projected, "https://text.egwwritings.org/book/b14389")
        self.assertEqual(baixar._book_id_from_url(projected), "14389")
        self.assertEqual(
            baixar._book_id_from_url("https://text.egwwritings.org/read/14389.102"),
            "14389",
        )

    def test_previous_navigation_accepts_editorial_block_alias(self) -> None:
        previous = CatalogSegment(
            remote_id="14623.11",
            url="https://text.egwwritings.org/read/14623.2",
            order=1,
            title="A vitória da esperança",
            html="<p>Texto</p>",
        )
        self.assertTrue(
            baixar._previous_segment_matches(
                previous,
                {"https://text.egwwritings.org/read/14623.11"},
            )
        )
        self.assertTrue(
            baixar._previous_segment_matches(
                previous,
                {"https://text.egwwritings.org/read/14623.2?origem=reader#top"},
            )
        )
        self.assertFalse(
            baixar._previous_segment_matches(
                previous,
                {"https://text.egwwritings.org/read/14623.30"},
            )
        )

    def test_detail_page_discovers_every_enabled_native_asset(self) -> None:
        def element(
            text: str = "",
            href: str | None = None,
            disabled: bool = False,
            content: str | None = None,
        ):
            value = Mock(text=text)
            value.get_attribute.side_effect = lambda name: (
                href
                if name == "href"
                else (content if name == "content" else None)
                if name == "content"
                else ("true" if name == "disabled" and disabled else None)
            )
            return value

        title = element("Atos dos Apóstolos")
        author = element("By Ellen G. White")
        cover = element(content="https://a.egwwritings.org/covers/1806?type=large")
        links = [
            element(href="https://media2.egwwritings.org/pdf/pt_AA(AA).pdf"),
            element(href="https://media2.egwwritings.org/epub/pt_AA(AA).epub"),
            element(href="https://media2.egwwritings.org/epub/disabled.epub", disabled=True),
            element(href="https://text.egwwritings.org/read/1806.2"),
        ]
        driver = _FakeDriver()

        def find_elements(by, selector):
            if by == _FakeBy.TAG_NAME and selector == "a":
                return links
            if selector == ".breadcrumbs-header-title":
                return [title]
            if selector == ".book-info-content__subtitle__author":
                return [author]
            if selector == "meta[property='og:image']":
                return [cover]
            return []

        driver.find_elements = Mock(side_effect=find_elements)
        with tempfile.TemporaryDirectory() as temporary:
            manager = baixar.BrowserSessionManager(
                _runtime(Mock(return_value=driver)),
                {"delay_seconds": 2.0, "browser_visible": True},
                self._runtime_paths(Path(temporary)),
            )
            manager._driver = driver
            manager._primary_handle = "main"
            with patch.object(manager, "_wait_for_human_release", return_value=driver):
                item = manager._enrich_book(
                    {
                        "id": "pt-br-livros",
                        "name": "Livros",
                        "category_name": "Escritos de Ellen White",
                        "category": "egw",
                        "language": "pt-BR",
                        "type": "livros",
                        "default_author_key": "egw",
                        "default_author_name": "Ellen G. White",
                    },
                    "https://text.egwwritings.org/book/b1806",
                    "Atos",
                    "",
                    Mock(before_request=Mock()),
                )
        self.assertEqual([asset.format for asset in item.assets], ["epub", "pdf"])
        self.assertEqual(len(item.assets), 2)
        self.assertEqual(item.author_name, "Ellen G. White")
        self.assertEqual(
            item.cover_url,
            "https://a.egwwritings.org/covers/1806?type=large",
        )

    def test_official_cover_is_normalized_without_upscale_or_metadata(self) -> None:
        from PIL import Image

        source = io.BytesIO()
        image = Image.new("RGB", (1600, 400), (35, 70, 105))
        image.save(source, format="JPEG", quality=95, exif=b"Exif\x00\x00fixture")
        payload = source.getvalue()
        response = Mock(
            status_code=200,
            headers={
                "content-length": str(len(payload)),
                "content-type": "image/jpeg",
            },
        )
        response.iter_content.return_value = [payload]
        session = Mock()
        session.get.return_value = response
        item = CatalogItem(
            remote_id="14389",
            collection_id="pt-br-pioneiros",
            collection_name="Pioneiros",
            author_name="Alonzo Trevier Jones",
            author_key="alonzo-trevier-jones",
            language_original="pt-BR",
            language="pt-BR",
            language_path="pt-br",
            publication_type="livros",
            title_original="Estudos Sobre a Fé",
            title_normalized="Estudos Sobre a Fé",
            public_url="https://text.egwwritings.org/book/b14389",
            cover_url="https://a.egwwritings.org/covers/14389?type=large",
        )
        config = {
            "allowed_asset_hosts": ["a.egwwritings.org", "media4.egwwritings.org"],
            "max_redirects": 2,
            "max_attempts": 1,
            "connect_timeout_seconds": 1,
            "read_timeout_seconds": 1,
            "chunk_bytes": 262144,
            "max_cover_bytes": 2_000_000,
            "cover_max_dimension": 800,
            "cover_max_pixels": 4_000_000,
            "delay_seconds": 0,
            "jitter_min_seconds": 0,
            "jitter_max_seconds": 0,
            "backoff_base_seconds": 0,
            "backoff_cap_seconds": 0,
            "retry_after_cap_seconds": 0,
            "_rate_limiter": Mock(before_request=Mock()),
        }
        with tempfile.TemporaryDirectory() as temporary, patch.object(
            baixar, "_validate_public_dns", return_value=None
        ):
            path, source_record, derivation = baixar.download_cover(
                session,
                item,
                Path(temporary),
                config,
            )
            self.assertEqual(baixar.validate_cover_png(path, config), (800, 200))
            with Image.open(path) as normalized:
                self.assertFalse(normalized.info)
            self.assertEqual(source_record["url"], item.cover_url)
            self.assertEqual(derivation["path"], "cover.png")
            self.assertEqual(derivation["hashes"]["sha256"], hash_file(path).sha256)

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

    def test_browser_manager_reuses_visible_persistent_tab(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            driver = _FakeDriver()
            firefox = Mock(return_value=driver)
            runtime = _runtime(firefox)
            profile = "constructor/.state/test-browser-profile"
            manager = baixar.BrowserSessionManager(
                runtime,
                {
                    "delay_seconds": 2.0,
                    "browser_visible": True,
                    "browser_wait_interval_seconds": 1.0,
                },
                self._runtime_paths(Path(temporary)),
            )
            collection_a = {
                "id": "a",
                "catalog_url": "https://egwwritings.org/allCollection/pt/245",
            }
            collection_b = {
                "id": "b",
                "catalog_url": "https://egwwritings.org/allCollection/en/4",
            }
            with patch.object(
                baixar,
                "_catalog_item_from_element",
                return_value=Mock(),
            ):
                manager.discover_catalog_items(collection_a, Mock(before_request=Mock()))
                manager.discover_catalog_items(collection_b, Mock(before_request=Mock()))
            self.assertEqual(firefox.call_count, 1)
            options = firefox.call_args.kwargs["options"]
            self.assertIn("-profile", options.arguments)
            self.assertNotIn("--headless", options.arguments)
            self.assertEqual(
                driver.visited,
                [
                    "https://text.egwwritings.org/allCollection/pt/245",
                    "https://text.egwwritings.org/allCollection/en/4",
                ],
            )
            manager.close()
            self.assertEqual(driver.quit_count, 1)

    def test_browser_challenge_detaches_for_human_and_resumes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            challenged = _FakeDriver(
                ["<html><title>Checking your browser</title><div>captcha</div></html>"]
            )
            resumed = _FakeDriver(["<html><div class='book-list-item'></div></html>"])
            firefox = Mock(side_effect=[challenged, resumed])
            runtime = _runtime(firefox)
            manager = baixar.BrowserSessionManager(
                runtime,
                {
                    "delay_seconds": 2.0,
                    "browser_visible": True,
                    "browser_handoff_enabled": True,
                    "browser_wait_interval_seconds": 1.0,
                    "browser_human_wait_seconds": 5.0,
                },
                self._runtime_paths(Path(temporary)),
            )
            process = _FakeProcess()

            def detached_process(*_args, **_kwargs):
                self.assertEqual(challenged.quit_count, 1)
                self.assertIsNone(manager._driver)
                return process

            with patch.object(manager, "_human_browser_binary", return_value="firefox"):
                with patch.object(baixar.subprocess, "Popen", side_effect=detached_process):
                    with patch.object(baixar.time, "sleep") as sleep_mock:
                        with patch.object(
                            baixar,
                            "_catalog_item_from_element",
                            return_value=Mock(),
                        ):
                            manager.discover_catalog_items(
                                {
                                    "id": "a",
                                    "catalog_url": "https://egwwritings.org/allCollection/pt/245",
                                },
                                Mock(before_request=Mock()),
                            )
            sleep_mock.assert_any_call(1.0)
            self.assertEqual(firefox.call_count, 2)
            self.assertEqual(challenged.quit_count, 1)
            self.assertEqual(
                resumed.visited,
                ["https://text.egwwritings.org/allCollection/pt/245"],
            )
            manager.close()

    def test_browser_handoff_disabled_stops_without_polling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            driver = _FakeDriver(
                ["<html><title>Checking your browser</title><div>captcha</div></html>"]
            )
            manager = baixar.BrowserSessionManager(
                _runtime(Mock(return_value=driver)),
                {
                    "delay_seconds": 2.0,
                    "browser_visible": True,
                    "browser_handoff_enabled": False,
                    "browser_wait_interval_seconds": 1.0,
                },
                self._runtime_paths(Path(temporary)),
            )
            with patch.object(baixar.subprocess, "Popen") as popen:
                with self.assertRaises(baixar.OriginBlocked):
                    manager.discover_catalog_items(
                        {
                            "id": "a",
                            "catalog_url": "https://egwwritings.org/allCollection/pt/245",
                        },
                        Mock(before_request=Mock()),
                    )
            popen.assert_not_called()
            manager.close()

    def test_browser_handoff_waits_for_delegated_profile_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manager = baixar.BrowserSessionManager(
                _runtime(Mock()),
                {
                    "delay_seconds": 2.0,
                    "browser_visible": True,
                    "browser_handoff_enabled": True,
                    "browser_wait_interval_seconds": 1.0,
                    "browser_human_wait_seconds": 10.0,
                },
                self._runtime_paths(root),
            )
            manager.profile_dir.mkdir(parents=True, exist_ok=True)
            profile_lock = manager.profile_dir / "parent.lock"
            profile_lock.write_bytes(b"")
            process = _FakeProcess()
            sleeps = 0

            def release_lock(_seconds: float) -> None:
                nonlocal sleeps
                sleeps += 1
                if sleeps == 3:
                    profile_lock.unlink()

            with patch.object(manager, "_human_browser_binary", return_value="firefox"):
                with patch.object(baixar.subprocess, "Popen", return_value=process):
                    with patch.object(baixar.time, "sleep", side_effect=release_lock):
                        manager._handoff_to_human(
                            "a",
                            "https://egwwritings.org/allCollection/pt/245",
                        )

            self.assertGreaterEqual(sleeps, 3)
            self.assertFalse(profile_lock.exists())

    def test_browser_rejects_challenge_reappearing_after_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            challenged = _FakeDriver(
                ["<html><title>Checking your browser</title><div>captcha</div></html>"]
            )
            resumed = _FakeDriver(
                ["<html><title>Checking your browser</title><div>captcha</div></html>"]
            )
            manager = baixar.BrowserSessionManager(
                _runtime(Mock(side_effect=[challenged, resumed])),
                {
                    "delay_seconds": 2.0,
                    "browser_visible": True,
                    "browser_handoff_enabled": True,
                    "browser_wait_interval_seconds": 1.0,
                    "browser_human_wait_seconds": 5.0,
                },
                self._runtime_paths(Path(temporary)),
            )
            with patch.object(manager, "_human_browser_binary", return_value="firefox"):
                with patch.object(baixar.subprocess, "Popen", return_value=_FakeProcess()):
                    with patch.object(baixar.time, "sleep"):
                        with self.assertRaises(baixar.OriginBlocked):
                            manager.discover_catalog_items(
                                {
                                    "id": "a",
                                    "catalog_url": "https://egwwritings.org/allCollection/pt/245",
                                },
                                Mock(before_request=Mock()),
                            )
            manager.close()


if __name__ == "__main__":
    unittest.main()
