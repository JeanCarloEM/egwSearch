# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Baixa colecoes EGW diretamente na estrutura canônica.

Dependencias de rede e navegador sao carregadas somente pela CLI. Importar este
modulo e seguro para testes, indexadores e ferramentas de migracao.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
from urllib.parse import urljoin, urlsplit

from publication_contract import (
    ContractError,
    DEFAULT_CONFIG_PATH,
    REPOSITORY_ROOT,
    build_source_document,
    choose_variant_path,
    format_from_url,
    hash_file,
    load_config,
    publication_identity,
    read_source_records,
    resolve_repository_path,
    validate_file_signature,
    validate_source_url,
    write_json_atomic,
)


class DownloadError(RuntimeError):
    """Representa falha conclusiva e sanitizada de aquisicao."""


_metadata_locks: dict[str, threading.Lock] = {}
_metadata_locks_guard = threading.Lock()


def _metadata_lock(path: Path) -> threading.Lock:
    key = str(path.resolve()).casefold()
    with _metadata_locks_guard:
        return _metadata_locks.setdefault(key, threading.Lock())


def _runtime_dependencies() -> dict:
    """Carrega integracoes opcionais sem contaminar importacao do contrato."""

    try:
        import requests
        from tqdm import tqdm
        from selenium import webdriver
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.by import By
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
    except ImportError as error:
        raise ContractError(
            "dependencias ausentes; instalar Requests, tqdm e Selenium no ambiente da CLI"
        ) from error
    return {
        "requests": requests,
        "tqdm": tqdm,
        "webdriver": webdriver,
        "ActionChains": ActionChains,
        "By": By,
        "FirefoxOptions": FirefoxOptions,
        "EC": EC,
        "WebDriverWait": WebDriverWait,
    }


def _validate_public_dns(host: str) -> None:
    """Rejeita resolucao local, privada, reservada ou nao global."""

    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        }
    except OSError as error:
        raise DownloadError(f"DNS indisponivel para {host}") from error
    if not addresses:
        raise DownloadError(f"DNS sem endereco para {host}")
    for address in addresses:
        parsed = ipaddress.ip_address(address)
        if not parsed.is_global:
            raise DownloadError(f"DNS nao publico bloqueado para {host}: {address}")


def _validate_network_url(url: str, allowed_hosts: set[str], require_format: bool) -> str:
    if require_format:
        validate_source_url(url, allowed_hosts=allowed_hosts, https_only=True)
    else:
        parsed = urlsplit(url)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.fragment
            or parsed.hostname.casefold() not in allowed_hosts
        ):
            raise ContractError(f"URL de catalogo nao permitida: {url}")
    _validate_public_dns(urlsplit(url).hostname or "")
    return url


def _request_asset(session, initial_url: str, download_config: dict):
    """Executa GET com redirecionamento manual e revalidacao integral."""

    allowed_hosts = {item.casefold() for item in download_config["allowed_asset_hosts"]}
    current = initial_url
    expected_format = format_from_url(initial_url)
    for redirect_count in range(download_config["max_redirects"] + 1):
        _validate_network_url(current, allowed_hosts, require_format=True)
        response = session.get(
            current,
            stream=True,
            allow_redirects=False,
            timeout=(
                download_config["connect_timeout_seconds"],
                download_config["read_timeout_seconds"],
            ),
        )
        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("location")
            response.close()
            if not location or redirect_count == download_config["max_redirects"]:
                raise DownloadError("redirecionamento ausente ou acima do limite")
            current = urljoin(current, location)
            if format_from_url(current) != expected_format:
                raise DownloadError("redirecionamento alterou o formato esperado")
            continue
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            raise DownloadError(f"HTTP {response.status_code} em aquisicao")
        return response, current, expected_format
    raise DownloadError("limite de redirecionamentos excedido")


def _stream_to_temporary(
    session,
    url: str,
    destination_directory: Path,
    download_config: dict,
    tqdm_factory,
) -> tuple[Path, dict, str, str]:
    """Transfere resposta limitada, calcula hashes e preserva parcial isolado."""

    response, final_url, publication_format = _request_asset(
        session, url, download_config
    )
    declared_size = response.headers.get("content-length")
    if declared_size:
        try:
            if int(declared_size) > download_config["max_bytes"]:
                response.close()
                raise DownloadError("Content-Length acima do limite")
        except ValueError as error:
            response.close()
            raise DownloadError("Content-Length invalido") from error
    destination_directory.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".download-",
        suffix=f".{publication_format}.partial",
        dir=destination_directory,
    )
    algorithms = {
        "sha1": hashlib.sha1(usedforsecurity=False),
        "sha256": hashlib.sha256(),
        "sha512": hashlib.sha512(),
    }
    size = 0
    temporary = Path(temporary_name)
    try:
        progress = tqdm_factory(
            desc=destination_directory.name,
            total=int(declared_size or 0),
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            leave=False,
        )
    except Exception:
        os.close(descriptor)
        temporary.unlink(missing_ok=True)
        response.close()
        raise
    try:
        with os.fdopen(descriptor, "wb") as stream:
            for chunk in response.iter_content(chunk_size=download_config["chunk_bytes"]):
                if not chunk:
                    continue
                size += len(chunk)
                if size > download_config["max_bytes"]:
                    raise DownloadError("resposta excedeu limite de bytes")
                stream.write(chunk)
                for algorithm in algorithms.values():
                    algorithm.update(chunk)
                progress.update(len(chunk))
            stream.flush()
            os.fsync(stream.fileno())
        if size == 0:
            raise DownloadError("resposta vazia")
        if declared_size and size != int(declared_size):
            raise DownloadError("corpo parcial diverge de Content-Length")
        validate_file_signature(temporary, publication_format)
        return (
            temporary,
            {
                "sha1": algorithms["sha1"].hexdigest(),
                "sha256": algorithms["sha256"].hexdigest(),
                "sha512": algorithms["sha512"].hexdigest(),
                "size": size,
            },
            final_url,
            publication_format,
        )
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    finally:
        response.close()
        progress.close()


def download_asset(
    session,
    url: str,
    identity,
    source_root: Path,
    download_config: dict,
    tqdm_factory,
) -> tuple[Path, dict, bool]:
    """Incorpora asset e retorna path, evidencia v2 e flag de instalacao."""

    destination_directory = source_root / identity.relative_directory()
    temporary, evidence, _final_url, publication_format = _stream_to_temporary(
        session,
        url,
        destination_directory,
        download_config,
        tqdm_factory,
    )
    base_path = destination_directory / identity.asset_name(publication_format)
    try:
        target, duplicate = choose_variant_path(base_path, evidence["sha256"])
        installed = not duplicate
        if duplicate:
            temporary.unlink()
        else:
            os.replace(temporary, target)
        record = {
            "format": publication_format,
            "url": url,
            "accessed_at": datetime.now(timezone.utc).isoformat(),
            "size": evidence["size"],
            "hashes": {
                "sha1": evidence["sha1"],
                "sha256": evidence["sha256"],
                "sha512": evidence["sha512"],
            },
        }
        return target, record, installed
    finally:
        temporary.unlink(missing_ok=True)


def _complete_legacy_records(
    records: list[dict],
    identity,
    destination_directory: Path,
) -> list[dict]:
    """Completa hashes legados somente a partir do asset local correlato."""

    completed = []
    for record in records:
        hashes = record.get("hashes") or {}
        if (
            hashes.get("sha1")
            and hashes.get("sha256")
            and hashes.get("sha512")
            and record.get("size")
        ):
            completed.append(record)
            continue
        base = destination_directory / identity.asset_name(record["format"])
        candidates = ([base] if base.is_file() else []) + sorted(
            destination_directory.glob(
                f"{identity.acronym}.*.{record['format']}"
            )
        )
        expected_sha256 = hashes.get("sha256")
        selected = None
        for candidate in candidates:
            candidate_hashes = hash_file(candidate)
            if expected_sha256 and candidate_hashes.sha256 != expected_sha256:
                continue
            if selected is not None:
                raise ContractError(
                    f"metadado legado ambiguo para {record['format']}"
                )
            selected = candidate_hashes
        if selected is None:
            raise ContractError(f"asset ausente para metadado {record['format']}")
        completed.append(
            {
                **record,
                "size": selected.size,
                "hashes": selected.as_dict(),
            }
        )
    return completed


def update_metadata(source_root: Path, identity, new_records: list[dict]) -> Path:
    """Mescla fontes sob lock local e grava documento fechado atomicamente."""

    destination_directory = source_root / identity.relative_directory()
    metadata_path = destination_directory / identity.metadata_name()
    with _metadata_lock(metadata_path):
        existing = []
        if metadata_path.exists():
            existing = _complete_legacy_records(
                read_source_records(metadata_path),
                identity,
                destination_directory,
            )
        document = build_source_document(identity, existing + new_records)
        write_json_atomic(metadata_path, document)
    return metadata_path


def _process_collection(collection: dict, config: dict, source_root: Path, runtime: dict) -> dict:
    """Descobre candidatos de uma colecao e baixa seus formatos conhecidos."""

    download_config = config["download"]
    allowed_catalog_hosts = {
        item.casefold() for item in download_config["allowed_catalog_hosts"]
    }
    _validate_network_url(
        collection["catalog_url"],
        allowed_catalog_hosts,
        require_format=False,
    )
    options = runtime["FirefoxOptions"]()
    options.add_argument("--headless")
    driver = runtime["webdriver"].Firefox(options=options)
    session = runtime["requests"].Session()
    session.headers["User-Agent"] = "egwSearch/FT-004 (+https://github.com/JeanCarloEM/egwSearch)"
    books_seen = assets_downloaded = failures = 0
    try:
        driver.set_window_size(1920, 1080)
        wait = runtime["WebDriverWait"](driver, 15)
        actions = runtime["ActionChains"](driver)
        driver.get(collection["catalog_url"])
        try:
            cookie = wait.until(
                runtime["EC"].presence_of_element_located(
                    (
                        runtime["By"].CSS_SELECTOR,
                        "div[class^='Ripple_root__lmfsr Ripple_dark__']",
                    )
                )
            )
            actions.move_to_element(cookie).click().perform()
        except Exception:
            pass
        last_height = driver.execute_script("return document.body.scrollHeight")
        stable = 0
        while stable < 3:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            current_height = driver.execute_script("return document.body.scrollHeight")
            stable = stable + 1 if current_height == last_height else 0
            last_height = current_height
        wait.until(
            runtime["EC"].presence_of_element_located(
                (
                    runtime["By"].CLASS_NAME,
                    "ReactVirtualized__Grid__innerScrollContainer",
                )
            )
        )
        books = driver.find_elements(runtime["By"].CLASS_NAME, "book-list-item")
        for book in books:
            books_seen += 1
            try:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", book
                )
                actions.move_to_element(book).perform()
                title_elements = book.find_elements(runtime["By"].CLASS_NAME, "title")
                if not title_elements:
                    raise ContractError("livro sem titulo candidato")
                title = title_elements[0].text
                identity = publication_identity(
                    "egw",
                    collection["language"],
                    collection["type"],
                    title,
                )
                panels = book.find_elements(
                    runtime["By"].CLASS_NAME, "book-download-links"
                )
                if not panels:
                    raise ContractError("painel de download ausente")
                records = []
                installed_assets = []
                try:
                    for link in panels[0].find_elements(runtime["By"].TAG_NAME, "a"):
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        try:
                            format_from_url(href)
                        except ContractError:
                            continue
                        target, record, installed = download_asset(
                            session,
                            href,
                            identity,
                            source_root,
                            download_config,
                            runtime["tqdm"],
                        )
                        records.append(record)
                        if installed:
                            installed_assets.append(target)
                        assets_downloaded += 1
                        print(
                            f"DOWNLOAD_OK collection={collection['id']} "
                            f"title={json.dumps(identity.title, ensure_ascii=False)} "
                            f"path={target.relative_to(REPOSITORY_ROOT).as_posix()}"
                        )
                    if records:
                        update_metadata(source_root, identity, records)
                except Exception:
                    for installed_asset in reversed(installed_assets):
                        installed_asset.unlink(missing_ok=True)
                    raise
            except Exception as error:
                failures += 1
                print(
                    f"DOWNLOAD_FAIL collection={collection['id']} "
                    f"item={books_seen} error={type(error).__name__}:{error}",
                    file=sys.stderr,
                )
        return {
            "collection": collection["id"],
            "books": books_seen,
            "assets": assets_downloaded,
            "failures": failures,
        }
    finally:
        session.close()
        driver.quit()


def _selected_collections(config: dict, selected: set[str] | None) -> list[dict]:
    collections = [
        collection
        for author in config["authors"].values()
        for collection in author["collections"]
    ]
    if not selected:
        return collections
    available = {collection["id"] for collection in collections}
    unknown = selected - available
    if unknown:
        raise ContractError(f"colecao desconhecida: {', '.join(sorted(unknown))}")
    return [collection for collection in collections if collection["id"] in selected]


def run(config_path: Path, selected: set[str] | None, workers: int | None) -> int:
    config = load_config(config_path)
    source_root = resolve_repository_path(config["source_root"], REPOSITORY_ROOT)
    runtime = _runtime_dependencies()
    collections = _selected_collections(config, selected)
    worker_count = workers or config["download"]["workers"]
    if worker_count < 1 or worker_count > len(collections):
        raise ContractError("workers fora do intervalo de colecoes")
    results = []
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(
                _process_collection,
                collection,
                config,
                source_root,
                runtime,
            ): collection["id"]
            for collection in collections
        }
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["collection"])
    print(json.dumps({"collections": results}, ensure_ascii=False, sort_keys=True))
    return 1 if any(item["failures"] for item in results) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Baixa publicacoes EGW na estrutura canônica.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument(
        "--collection",
        action="append",
        dest="collections",
        help="ID de colecao; repetivel. Omitido processa todas.",
    )
    parser.add_argument("--workers", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        return run(
            Path(arguments.config).resolve(),
            set(arguments.collections) if arguments.collections else None,
            arguments.workers,
        )
    except ContractError as error:
        print(f"ERRO_CONTRATO: {error}", file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("CANCELADO", file=sys.stderr)
        return 130
    except Exception as error:
        print(f"ERRO_OPERACIONAL: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
