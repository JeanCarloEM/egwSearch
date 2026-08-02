# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Testes sem rede do downloader canônico."""

from __future__ import annotations

import io
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "scripts" / "publications"
sys.path.insert(0, str(CONTRACT_ROOT))

import baixar  # noqa: E402
from acquisition import (  # noqa: E402
    AcquisitionLedger,
    CatalogAsset,
    CatalogItem,
    CatalogSegment,
    build_source_v3,
)
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

    @staticmethod
    def _checkpoint_item(remote_id: str, title: str) -> CatalogItem:
        return CatalogItem(
            remote_id=remote_id,
            collection_id="pt-br-livros",
            collection_name="Escritos de Ellen White - Livros",
            author_name="Ellen G. White",
            author_key="egw",
            language_original="pt-BR",
            language="pt-BR",
            language_path="pt-br",
            publication_type="livros",
            title_original=title,
            title_normalized=title,
            public_url=f"https://text.egwwritings.org/book/b{remote_id}",
            category_name="Escritos de Ellen White",
            category_path="egw",
            assets=(
                CatalogAsset(
                    "epub",
                    f"https://media2.egwwritings.org/epub/pt_{remote_id}.epub",
                ),
            ),
        )

    @staticmethod
    def _checkpoint_collection() -> dict:
        return {
            "id": "pt-br-livros",
            "name": "Escritos de Ellen White - Livros",
            "catalog_url": "https://egwwritings.org/allCollection/pt/4",
            "language": "pt-BR",
            "type": "livros",
            "category_name": "Escritos de Ellen White",
            "category": "egw",
        }

    @staticmethod
    def _checkpoint_config() -> dict:
        return {
            "download": {
                "allowed_catalog_hosts": [
                    "egwwritings.org",
                    "text.egwwritings.org",
                ],
                "delay_seconds": 2,
                "jitter_min_seconds": 0,
                "jitter_max_seconds": 0,
            }
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

    def test_collection_discovery_resumes_without_reloading_catalog(self) -> None:
        collection = self._checkpoint_collection()
        first = self._checkpoint_item("1", "Primeiro")
        second = self._checkpoint_item("2", "Segundo")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint_path = baixar._collection_checkpoint_path(
                root, collection, None, None
            )
            checkpoint = baixar._new_collection_checkpoint(collection, None, None)
            checkpoint["catalog_entries"] = [
                {
                    "title": first.title_original,
                    "url": first.public_url,
                    "author": first.author_name,
                },
                {
                    "title": second.title_original,
                    "url": second.public_url,
                    "author": second.author_name,
                },
            ]
            checkpoint["items"] = [baixar._catalog_item_record(first)]
            baixar._save_collection_checkpoint(checkpoint_path, checkpoint)
            loaded = baixar._load_collection_checkpoint(
                checkpoint_path, collection, None, None
            )
            manager = baixar.BrowserSessionManager(
                _runtime(Mock()),
                {"delay_seconds": 2, "browser_visible": True},
                self._runtime_paths(root),
            )
            with patch.object(
                manager, "_discover_catalog_links"
            ) as catalog, patch.object(
                manager, "_enrich_book", return_value=second
            ) as enrich:
                items = manager.discover_catalog_items(
                    collection,
                    Mock(before_request=Mock()),
                    checkpoint_path=checkpoint_path,
                    checkpoint=loaded,
                )
            self.assertEqual(items, [first, second])
            catalog.assert_not_called()
            enrich.assert_called_once()
            completed = baixar._load_collection_checkpoint(
                checkpoint_path, collection, None, None
            )
            self.assertTrue(completed["discovery_complete"])

    def test_collection_processing_resumes_only_unconfirmed_item(self) -> None:
        collection = self._checkpoint_collection()
        items = [
            self._checkpoint_item("1", "Primeiro"),
            self._checkpoint_item("2", "Segundo"),
        ]
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary)
            state_root = root / "state"
            source_root = root / "publications"
            checkpoint_path = baixar._collection_checkpoint_path(
                state_root, collection, None, None
            )
            checkpoint = baixar._new_collection_checkpoint(collection, None, None)
            checkpoint["catalog_entries"] = [
                {
                    "title": item.title_original,
                    "url": item.public_url,
                    "author": item.author_name,
                }
                for item in items
            ]
            checkpoint["items"] = [baixar._catalog_item_record(item) for item in items]
            checkpoint["discovery_complete"] = True
            baixar._save_collection_checkpoint(checkpoint_path, checkpoint)
            completed = {
                "state": "completed",
                "downloaded": 1,
                "skipped": 0,
                "extracted": 0,
                "converted": 0,
            }
            with patch.object(
                baixar,
                "_process_catalog_item",
                side_effect=[completed, KeyboardInterrupt()],
            ):
                with self.assertRaises(KeyboardInterrupt):
                    baixar._process_collection(
                        collection,
                        self._checkpoint_config(),
                        source_root,
                        state_root,
                        None,
                        no_network=True,
                        fixture_payload={"publications": []},
                    )
            interrupted = baixar._load_collection_checkpoint(
                checkpoint_path, collection, None, None
            )
            self.assertEqual(interrupted["confirmed_remote_ids"], ["1"])
            with patch.object(
                baixar, "_process_catalog_item", return_value=completed
            ) as process:
                summary = baixar._process_collection(
                    collection,
                    self._checkpoint_config(),
                    source_root,
                    state_root,
                    None,
                    no_network=True,
                    fixture_payload={"publications": []},
                )
            self.assertEqual(summary["resumed"], 1)
            self.assertEqual(process.call_count, 1)
            self.assertEqual(process.call_args.args[0].remote_id, "2")
            self.assertFalse(checkpoint_path.exists())

    def test_completed_enrichment_is_promoted_before_later_interruption(self) -> None:
        collection = self._checkpoint_collection()
        first = self._checkpoint_item("14386", "Primeira obra completa")
        second = self._checkpoint_item("14382", "Segunda obra incompleta")
        completed = {
            "state": "completed",
            "downloaded": 0,
            "skipped": 0,
            "extracted": 1,
            "converted": 1,
        }
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary)
            state_root = root / "state"
            source_root = root / "publications"
            checkpoint_path = baixar._collection_checkpoint_path(
                state_root, collection, None, None
            )

            def discover(*_args, **kwargs):
                active = kwargs["checkpoint"] or baixar._new_collection_checkpoint(
                    collection, None, None
                )
                active["catalog_entries"] = [
                    {
                        "title": item.title_original,
                        "url": item.public_url,
                        "author": item.author_name,
                    }
                    for item in (first, second)
                ]
                active["items"] = [baixar._catalog_item_record(first)]
                active["_items"] = [first]
                baixar._save_collection_checkpoint(checkpoint_path, active)
                kwargs["on_item_ready"](first, 1, active)
                raise KeyboardInterrupt()

            browser = Mock()
            browser.discover_catalog_items.side_effect = discover
            with patch.object(
                baixar, "_validate_network_url"
            ), patch.object(
                baixar, "preflight_local_publication", return_value=None
            ), patch.object(
                baixar, "_process_catalog_item", return_value=completed
            ) as process:
                with self.assertRaises(KeyboardInterrupt):
                    baixar._process_collection(
                        collection,
                        self._checkpoint_config(),
                        source_root,
                        state_root,
                        None,
                        browser_manager=browser,
                    )

            interrupted = baixar._load_collection_checkpoint(
                checkpoint_path, collection, None, None
            )
            self.assertEqual(interrupted["confirmed_remote_ids"], ["14386"])
            self.assertFalse(interrupted["discovery_complete"])
            process.assert_called_once()
            self.assertEqual(process.call_args.args[0].remote_id, "14386")

    def test_stale_false_checkpoint_reapplies_current_local_gate(self) -> None:
        collection = self._checkpoint_collection()
        stale = self._checkpoint_item("11101", "Testemunhos para a Igreja 5")
        local = replace(stale, local_complete=True)
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary)
            state_root = root / "state"
            source_root = root / "publications"
            checkpoint_path = baixar._collection_checkpoint_path(
                state_root, collection, None, None
            )
            checkpoint = baixar._new_collection_checkpoint(collection, None, None)
            checkpoint["catalog_entries"] = [
                {
                    "title": stale.title_original,
                    "url": stale.public_url,
                    "author": stale.author_name,
                }
            ]
            checkpoint["items"] = [baixar._catalog_item_record(stale)]
            checkpoint["discovery_complete"] = True
            baixar._save_collection_checkpoint(checkpoint_path, checkpoint)
            result = {
                "state": "skipped",
                "downloaded": 0,
                "skipped": 1,
                "extracted": 0,
                "converted": 0,
            }
            browser = Mock()
            browser._enrich_book.side_effect = AssertionError(
                "checkpoint antigo não pode liberar request"
            )
            with patch.object(
                baixar, "preflight_local_publication", return_value=local
            ) as preflight, patch.object(
                baixar, "_process_catalog_item", return_value=result
            ) as process:
                baixar._process_collection(
                    collection,
                    self._checkpoint_config(),
                    source_root,
                    state_root,
                    None,
                    no_network=True,
                    fixture_payload={"publications": []},
                    browser_manager=browser,
                )
            preflight.assert_called_once()
            self.assertTrue(process.call_args.args[0].local_complete)
            browser._enrich_book.assert_not_called()

    def test_invalid_checkpoint_blocks_until_explicit_restart(self) -> None:
        collection = self._checkpoint_collection()
        item = self._checkpoint_item("1", "Primeiro")
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary)
            state_root = root / "state"
            source_root = root / "publications"
            checkpoint_path = baixar._collection_checkpoint_path(
                state_root, collection, None, None
            )
            checkpoint_path.parent.mkdir(parents=True)
            checkpoint_path.write_text("{invalido", encoding="utf-8")
            with self.assertRaisesRegex(baixar.ContractError, "use --restart"):
                baixar._process_collection(
                    collection,
                    self._checkpoint_config(),
                    source_root,
                    state_root,
                    None,
                    no_network=True,
                    fixture_payload={"publications": []},
                )
            completed = {
                "state": "completed",
                "downloaded": 1,
                "skipped": 0,
                "extracted": 0,
                "converted": 0,
            }
            with patch.object(
                baixar, "parse_catalog_payload", return_value=[item]
            ), patch.object(
                baixar, "_process_catalog_item", return_value=completed
            ):
                summary = baixar._process_collection(
                    collection,
                    self._checkpoint_config(),
                    source_root,
                    state_root,
                    None,
                    no_network=True,
                    fixture_payload={"publications": []},
                    restart=True,
                )
            self.assertEqual(summary["failures"], 0)
            self.assertFalse(checkpoint_path.exists())
            self.assertTrue(baixar.build_parser().parse_args(["--restart"]).restart)

    def test_intelligence_failure_preserves_unconfirmed_checkpoint(self) -> None:
        collection = self._checkpoint_collection()
        item = self._checkpoint_item("7", "Publicação analisável")
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            root = Path(temporary)
            source_root = root / "publications"
            state_root = root / "state"
            config = self._checkpoint_config()
            config["intelligence"] = {"index_path": "src/publications/index.json"}
            completed = {
                "state": "completed",
                "downloaded": 1,
                "skipped": 0,
                "extracted": 0,
                "converted": 0,
            }
            with patch.object(
                baixar, "parse_catalog_payload", return_value=[item]
            ), patch.object(
                baixar, "_process_catalog_item", return_value=completed
            ), patch.object(
                baixar,
                "finalize_publication_intelligence",
                side_effect=RuntimeError("análise inválida"),
            ) as finalize:
                summary = baixar._process_collection(
                    collection,
                    config,
                    source_root,
                    state_root,
                    None,
                    no_network=True,
                    fixture_payload={"publications": []},
                )
            self.assertEqual(summary["failures"], 1)
            checkpoint = baixar._load_collection_checkpoint(
                baixar._collection_checkpoint_path(
                    state_root, collection, None, None
                ),
                collection,
                None,
                None,
            )
            self.assertEqual(checkpoint["confirmed_remote_ids"], [])
            finalize.assert_called_once()
            ledger = AcquisitionLedger(state_root / "ledger.json")
            self.assertEqual(ledger.get(item.stable_key())["state"], "temporary_failure")
            self.assertEqual(
                ledger.get(item.stable_key())["phase"], "publication-intelligence"
            )

    def test_invalid_text_checkpoint_is_preserved_and_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkpoint = root / "acquisition" / "text" / "14623.json"
            checkpoint.parent.mkdir(parents=True)
            checkpoint.write_text("{invalido", encoding="utf-8")
            manager = baixar.BrowserSessionManager(
                _runtime(Mock()),
                {"delay_seconds": 2, "browser_visible": True},
                self._runtime_paths(root),
            )
            with self.assertRaisesRegex(baixar.ContractError, "use --restart"):
                manager._discover_text_segments(
                    "https://text.egwwritings.org/read/14623.2",
                    Mock(before_request=Mock()),
                )
            self.assertTrue(checkpoint.is_file())
            self.assertIsNone(manager._driver)

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

    def test_structured_missing_cover_generates_deterministic_technical_cover(self) -> None:
        problem = b'{"title":"Not Found","status":404,"detail":"Cover not found"}'

        def response():
            value = Mock(
                status_code=404,
                headers={"content-type": "application/problem+json"},
            )
            value.iter_content.return_value = [problem]
            return value

        session = Mock()
        session.get.side_effect = [response(), response()]
        item = CatalogItem(
            remote_id="14623",
            collection_id="pt-br-livros",
            collection_name="Escritos de Ellen White - Livros",
            author_name="Ellen G. White",
            author_key="egw",
            language_original="pt-BR",
            language="pt-BR",
            language_path="pt-br",
            publication_type="livros",
            title_original="A Vitória da Esperança",
            title_normalized="A Vitória da Esperança",
            public_url="https://text.egwwritings.org/book/b14623",
            category_name="Escritos de Ellen White",
            category_path="egw",
            cover_url="https://a.egwwritings.org/covers/14623?type=large",
        )
        config = {
            "allowed_asset_hosts": ["a.egwwritings.org"],
            "max_redirects": 1,
            "max_attempts": 1,
            "connect_timeout_seconds": 1,
            "read_timeout_seconds": 1,
            "chunk_bytes": 262144,
            "cover_max_dimension": 800,
            "_rate_limiter": Mock(before_request=Mock()),
        }
        with tempfile.TemporaryDirectory() as temporary, patch.object(
            baixar, "_validate_public_dns", return_value=None
        ):
            first, source, derivation = baixar.download_cover(
                session, item, Path(temporary), config
            )
            first_hash = hash_file(first).sha256
            second, _, second_derivation = baixar.download_cover(
                session, item, Path(temporary), config
            )
            self.assertEqual(first_hash, hash_file(second).sha256)
            self.assertEqual(source["status"], 404)
            self.assertEqual(source["method"], "official-cover-unavailable")
            self.assertEqual(derivation["method"], "deterministic-technical-cover")
            self.assertEqual(
                derivation["hashes"]["sha256"],
                second_derivation["hashes"]["sha256"],
            )

    def test_unstructured_404_does_not_generate_technical_cover(self) -> None:
        response = Mock(status_code=404, headers={"content-type": "text/html"})
        response.iter_content.return_value = [b"<html>not found</html>"]
        session = Mock(get=Mock(return_value=response))
        with patch.object(baixar, "_validate_public_dns", return_value=None):
            with self.assertRaisesRegex(baixar.DownloadError, "não comprova"):
                baixar._request_cover(
                    session,
                    "https://a.egwwritings.org/covers/14623?type=large",
                    {
                        "allowed_asset_hosts": ["a.egwwritings.org"],
                        "max_redirects": 1,
                        "max_attempts": 1,
                        "connect_timeout_seconds": 1,
                        "read_timeout_seconds": 1,
                        "_rate_limiter": Mock(before_request=Mock()),
                    },
                )

    def test_complete_local_publication_skips_detail_and_assets(self) -> None:
        item = CatalogItem(
            remote_id="1806",
            collection_id="pt-br-livros",
            collection_name="Escritos de Ellen White - Livros",
            author_name="Ellen G. White",
            author_key="egw",
            language_original="pt-BR",
            language="pt-BR",
            language_path="pt-br",
            publication_type="livros",
            title_original="Atos dos Apóstolos",
            title_normalized="Atos dos Apóstolos",
            public_url="https://text.egwwritings.org/book/b1806",
            category_name="Escritos de Ellen White",
            category_path="egw",
            local_complete=True,
        )
        driver = _FakeDriver()
        with tempfile.TemporaryDirectory() as temporary:
            manager = baixar.BrowserSessionManager(
                _runtime(Mock(return_value=driver)),
                {"delay_seconds": 0, "browser_visible": True},
                self._runtime_paths(Path(temporary)),
            )
            manager._driver = driver
            manager._primary_handle = "main"
            with patch.object(manager, "_wait_for_human_release", return_value=driver), patch.object(
                manager,
                "_discover_catalog_links",
                return_value={item.public_url: (item.title_original, item.public_url, item.author_name)},
            ), patch.object(manager, "_enrich_book") as enrich:
                discovered = manager.discover_catalog_items(
                    {
                        "id": "pt-br-livros",
                        "catalog_url": "https://egwwritings.org/allCollection/pt/4",
                    },
                    Mock(before_request=Mock()),
                    local_preflight=lambda remote_id, *_catalog: (
                        item if remote_id == "1806" else None
                    ),
                )
            self.assertEqual(discovered, [item])
            enrich.assert_not_called()
            self.assertEqual(
                driver.visited,
                ["https://text.egwwritings.org/allCollection/pt/4"],
            )

    def test_local_preflight_validates_whole_native_publication(self) -> None:
        collection = {
            "id": "pt-br-livros",
            "name": "Escritos de Ellen White - Livros",
        }
        item = CatalogItem(
            remote_id="1806",
            collection_id=collection["id"],
            collection_name=collection["name"],
            author_name="Ellen G. White",
            author_key="egw",
            language_original="pt-BR",
            language="pt-BR",
            language_path="pt-br",
            publication_type="livros",
            title_original="Atos dos Apóstolos",
            title_normalized="Atos dos Apóstolos",
            public_url="https://text.egwwritings.org/book/b1806",
            category_name="Escritos de Ellen White",
            category_path="egw",
        )
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            source_root = Path(temporary)
            identity = item.publication_identity()
            directory = source_root / identity.relative_directory()
            directory.mkdir(parents=True)
            epub = directory / identity.asset_name("epub")
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr(
                    "mimetype",
                    b"application/epub+zip",
                    compress_type=zipfile.ZIP_STORED,
                )
            evidence = hash_file(epub)
            url = "https://media2.egwwritings.org/epub/pt_AA.epub"
            document = build_source_v3(
                item,
                "completed",
                [{"format": "epub", "url": url, "size": evidence.size, "hashes": evidence.as_dict()}],
            )
            write_json_atomic(directory / identity.metadata_name(), document)
            index = baixar.build_local_publication_index(source_root)
            complete = baixar.preflight_local_publication(
                "1806", collection, source_root, index, {"cover_max_dimension": 800}
            )
            self.assertIsNotNone(complete)
            self.assertTrue(complete.local_complete)
            epub.write_bytes(b"corrompido")
            self.assertIsNone(
                baixar.preflight_local_publication(
                    "1806", collection, source_root, index, {"cover_max_dimension": 800}
                )
            )

    def test_legacy_pdf_epub_skip_every_book_request(self) -> None:
        collection = {
            "id": "en-books",
            "name": "EGW Writings - Books",
            "catalog_url": "https://egwwritings.org/allCollection/en/4",
            "language": "en",
            "type": "books",
            "category_name": "EGW Writings",
            "category": "egw",
            "default_author_key": "egw",
        }
        title = "Life Sketches of James White and Ellen G. White (1880 ed.)"
        public_url = "https://text.egwwritings.org/book/b42"
        with tempfile.TemporaryDirectory(dir=REPOSITORY_ROOT) as temporary:
            source_root = Path(temporary)
            identity = publication_identity(
                "egw", "en", "books", title, category="egw"
            )
            directory = (
                source_root
                / "egw"
                / "en-us"
                / "books"
                / identity.route_slug
            )
            directory.mkdir(parents=True)
            pdf = directory / identity.asset_name("pdf")
            pdf.write_bytes(b"%PDF-1.7\ncomplete\n%%EOF")
            epub = directory / identity.asset_name("epub")
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr(
                    "mimetype",
                    b"application/epub+zip",
                    compress_type=zipfile.ZIP_STORED,
                )
            pdf_url = "https://media2.egwwritings.org/pdf/en_LS80.pdf"
            epub_url = "https://media2.egwwritings.org/epub/en_LS80.epub"
            write_json_atomic(
                directory / identity.metadata_name(),
                {
                    pdf_url: {"acesso": 1, "sha256": hash_file(pdf).sha256},
                    epub_url: {"acesso": 1, "sha256": hash_file(epub).sha256},
                },
            )
            driver = _FakeDriver()
            manager = baixar.BrowserSessionManager(
                _runtime(Mock(return_value=driver)),
                {"delay_seconds": 0, "browser_visible": True},
                self._runtime_paths(source_root),
            )
            manager._driver = driver
            manager._primary_handle = "main"
            local_index = baixar.build_local_publication_index(source_root)

            def local_preflight(remote_id, card_title, card_url, card_author):
                return baixar.preflight_local_publication(
                    remote_id,
                    collection,
                    source_root,
                    local_index,
                    {},
                    card_title,
                    card_url,
                    card_author,
                )

            with patch.object(
                manager, "_wait_for_human_release", return_value=driver
            ), patch.object(
                manager,
                "_discover_catalog_links",
                return_value={public_url: (title, public_url, "Ellen G. White")},
            ), patch.object(
                manager,
                "_enrich_book",
                side_effect=AssertionError("request individual proibido"),
            ) as enrich:
                discovered = manager.discover_catalog_items(
                    collection,
                    Mock(before_request=Mock()),
                    local_preflight=local_preflight,
                )
            self.assertEqual(len(discovered), 1)
            self.assertTrue(discovered[0].local_complete)
            self.assertEqual(
                {asset.format for asset in discovered[0].assets}, {"pdf", "epub"}
            )
            enrich.assert_not_called()
            self.assertEqual(
                driver.visited,
                ["https://text.egwwritings.org/allCollection/en/4"],
            )

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

    def test_download_blocks_same_sha512_in_another_publication(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary)
            identity = publication_identity(
                "egw", "pt-br", "livros", "Nova", category="egw"
            )
            existing = (
                source_root / "egw" / "pt-br" / "livros" / "canonica" / "c.pdf"
            )
            existing.parent.mkdir(parents=True)
            existing.write_bytes(b"%PDF-1.7\nidentical\n%%EOF")
            evidence = hash_file(existing)

            def fake_stream(*_args, **_kwargs):
                destination = source_root / identity.relative_directory()
                destination.mkdir(parents=True, exist_ok=True)
                partial = destination / ".fixture.pdf.partial"
                partial.write_bytes(existing.read_bytes())
                return (
                    partial,
                    {**evidence.as_dict(), "size": evidence.size},
                    "https://media2.egwwritings.org/pdf/nova.pdf",
                    "pdf",
                )

            index = {("pdf", evidence.sha256): [existing.resolve()]}
            with patch.object(baixar, "_stream_to_temporary", side_effect=fake_stream):
                with self.assertRaisesRegex(baixar.ContractError, "duplicaria publicacao"):
                    baixar.download_asset(
                        object(),
                        "https://media2.egwwritings.org/pdf/nova.pdf",
                        identity,
                        source_root,
                        {"_asset_identity_index": index},
                        lambda **_kwargs: _Progress(),
                    )
            self.assertFalse(
                (
                    source_root
                    / identity.relative_directory()
                    / identity.asset_name("pdf")
                ).exists()
            )

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
