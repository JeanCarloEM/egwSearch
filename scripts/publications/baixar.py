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

from acquisition import (
    AcquisitionLedger,
    CatalogAsset,
    CatalogItem,
    CatalogSegment,
    OriginBlocked,
    RateLimiter,
    RatePolicy,
    build_source_v3,
    canonical_author_key,
    canonical_language,
    canonical_publication_type,
    contains_block_marker,
    generate_epub,
    parse_catalog_payload,
    remote_id_from_url,
    validate_generated_epub,
    write_markdown_publication,
)
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


class NotModified(DownloadError):
    """Resposta condicional confirmou que o ativo remoto não mudou."""


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


def _validate_network_url(
    url: str,
    allowed_hosts: set[str],
    require_format: bool,
    *,
    resolve_dns: bool = True,
) -> str:
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
    if resolve_dns:
        _validate_public_dns(urlsplit(url).hostname or "")
    return url


def _request_asset(session, initial_url: str, download_config: dict):
    """Executa GET com redirecionamento manual e revalidacao integral."""

    allowed_hosts = {item.casefold() for item in download_config["allowed_asset_hosts"]}
    current = initial_url
    expected_format = format_from_url(initial_url)
    limiter = download_config.get("_rate_limiter")
    request_headers = dict(download_config.get("_conditional_headers") or {})
    for redirect_count in range(download_config["max_redirects"] + 1):
        _validate_network_url(current, allowed_hosts, require_format=True)
        response = _get_with_retry(
            session,
            current,
            download_config,
            limiter=limiter,
            headers=request_headers,
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
        if response.status_code == 304:
            response.close()
            raise NotModified("ativo remoto nao modificado")
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            raise DownloadError(f"HTTP {response.status_code} em aquisicao")
        return response, current, expected_format
    raise DownloadError("limite de redirecionamentos excedido")


def _rate_policy(download_config: dict) -> RatePolicy:
    return RatePolicy(
        delay_seconds=float(download_config.get("delay_seconds", 2.0)),
        jitter_min_seconds=float(download_config.get("jitter_min_seconds", 0.5)),
        jitter_max_seconds=float(download_config.get("jitter_max_seconds", 1.5)),
        max_attempts=int(download_config.get("max_attempts", 3)),
        backoff_base_seconds=float(download_config.get("backoff_base_seconds", 2.0)),
        backoff_cap_seconds=float(download_config.get("backoff_cap_seconds", 60.0)),
        retry_after_cap_seconds=float(
            download_config.get("retry_after_cap_seconds", 900.0)
        ),
    )


def _get_with_retry(
    session,
    url: str,
    download_config: dict,
    *,
    limiter: RateLimiter | None = None,
    headers: dict | None = None,
):
    """GET conservador com repetição limitada e parada imediata por contenção."""

    rate_limiter = limiter or RateLimiter(_rate_policy(download_config))
    maximum = int(download_config.get("max_attempts", 3))
    for attempt in range(1, maximum + 1):
        rate_limiter.before_request()
        try:
            response = session.get(
                url,
                stream=True,
                allow_redirects=False,
                headers=headers or None,
                timeout=(
                    download_config["connect_timeout_seconds"],
                    download_config["read_timeout_seconds"],
                ),
            )
        except Exception as error:
            if attempt >= maximum:
                raise DownloadError(
                    f"falha de rede apos {attempt} tentativa(s): {type(error).__name__}"
                ) from error
            rate_limiter.backoff(attempt)
            continue
        status = int(response.status_code)
        if status == 403:
            response.close()
            raise OriginBlocked("HTTP 403; coleta interrompida sem repeticao")
        if status in {408, 429} or 500 <= status <= 599:
            retry_after = response.headers.get("retry-after")
            response.close()
            if attempt >= maximum:
                raise DownloadError(
                    f"HTTP {status} persistente apos {attempt} tentativa(s)"
                )
            rate_limiter.backoff(attempt, retry_after if status == 429 else None)
            continue
        return response
    raise DownloadError("tentativas esgotadas")


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
                "etag": response.headers.get("etag") or "",
                "last_modified": response.headers.get("last-modified") or "",
                "mime": response.headers.get("content-type") or "",
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


def _identity_directories(source_root: Path, identity) -> list[Path]:
    directories = [source_root / identity.relative_directory()]
    if identity.language == "en":
        directories.append(
            source_root
            / identity.author
            / "en-us"
            / identity.publication_type
            / identity.route_slug
        )
    return directories


def _asset_candidates(directory: Path, identity, publication_format: str) -> list[Path]:
    base = directory / identity.asset_name(publication_format)
    return ([base] if base.is_file() else []) + sorted(
        path
        for path in directory.glob(f"{identity.acronym}.*.{publication_format}")
        if path.is_file()
    )


def preflight_existing_asset(
    url: str,
    identity,
    source_root: Path,
    remote_asset: CatalogAsset | None = None,
) -> tuple[Path, dict] | None:
    """Comprova ativo local por metadado+assinatura+tamanho+SHA antes da rede."""

    publication_format = format_from_url(url)
    for directory in _identity_directories(source_root, identity):
        metadata_path = directory / identity.metadata_name()
        if not metadata_path.is_file():
            continue
        records = read_source_records(metadata_path)
        matching = [
            record
            for record in records
            if record.get("format") == publication_format and record.get("url") == url
        ]
        for record in matching:
            hashes = record.get("hashes") or {}
            expected_sha256 = hashes.get("sha256")
            expected_size = record.get("size")
            if remote_asset is not None:
                if (
                    remote_asset.remote_hash
                    and remote_asset.remote_hash != expected_sha256
                ):
                    continue
                if remote_asset.size and remote_asset.size != expected_size:
                    continue
                if (
                    remote_asset.etag
                    and record.get("etag")
                    and remote_asset.etag != record.get("etag")
                ):
                    continue
                if (
                    remote_asset.last_modified
                    and record.get("last_modified")
                    and remote_asset.last_modified != record.get("last_modified")
                ):
                    continue
            if not re_full_sha256(expected_sha256):
                continue
            for candidate in _asset_candidates(directory, identity, publication_format):
                try:
                    if isinstance(expected_size, int) and candidate.stat().st_size != expected_size:
                        continue
                    validate_file_signature(candidate, publication_format)
                    evidence = hash_file(candidate)
                except (OSError, ContractError):
                    continue
                if evidence.sha256 != expected_sha256:
                    continue
                normalized = {
                    **record,
                    "size": evidence.size,
                    "hashes": evidence.as_dict(),
                    "result": "skipped",
                }
                return candidate, normalized
    return None


def re_full_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def download_asset(
    session,
    url: str,
    identity,
    source_root: Path,
    download_config: dict,
    tqdm_factory,
    remote_asset: CatalogAsset | None = None,
    revalidate: bool = False,
) -> tuple[Path, dict, bool]:
    """Incorpora asset e retorna path, evidencia v2 e flag de instalacao."""

    existing = preflight_existing_asset(
        url,
        identity,
        source_root,
        remote_asset=remote_asset,
    )
    if existing is not None and not revalidate:
        return existing[0], existing[1], False
    effective_config = dict(download_config)
    if existing is not None and revalidate:
        headers = {}
        if existing[1].get("etag"):
            headers["If-None-Match"] = existing[1]["etag"]
        if existing[1].get("last_modified"):
            headers["If-Modified-Since"] = existing[1]["last_modified"]
        if not headers:
            return existing[0], existing[1], False
        effective_config["_conditional_headers"] = headers
    destination_directory = source_root / identity.relative_directory()
    try:
        temporary, evidence, _final_url, publication_format = _stream_to_temporary(
            session,
            url,
            destination_directory,
            effective_config,
            tqdm_factory,
        )
    except NotModified:
        if existing is None:
            raise
        return existing[0], existing[1], False
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
            "method": "native-download",
            "accessed_at": datetime.now(timezone.utc).isoformat(),
            "size": evidence["size"],
            "etag": evidence.get("etag", ""),
            "last_modified": evidence.get("last_modified", ""),
            "mime": evidence.get("mime", ""),
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


def _first_element_text(book, runtime: dict, selectors: list[str]) -> str:
    for selector in selectors:
        elements = book.find_elements(runtime["By"].CSS_SELECTOR, selector)
        for element in elements:
            value = str(element.text or "").strip()
            if value:
                return value
    return ""


def _catalog_item_from_element(book, collection: dict, runtime: dict) -> CatalogItem:
    title = _first_element_text(book, runtime, [".title", "[class*='title']"])
    if not title:
        raise ContractError("livro sem titulo candidato")
    author = str(collection.get("default_author_name") or "").strip()
    if collection.get("discover_authors"):
        author = _first_element_text(
            book,
            runtime,
            [".author", ".book-author", "[class*='author']"],
        )
        if not author:
            raise ContractError("publicacao multiautor sem autor comprovado")
    public_url = ""
    assets: list[CatalogAsset] = []
    for link in book.find_elements(runtime["By"].TAG_NAME, "a"):
        href = str(link.get_attribute("href") or "").strip()
        if not href:
            continue
        try:
            publication_format = format_from_url(href)
        except ContractError:
            if re_search_book_url(href) and not public_url:
                public_url = href
            continue
        assets.append(CatalogAsset(format=publication_format, url=href))
    if not public_url:
        raise ContractError("publicacao sem URL publica ou identificador remoto")
    language, language_path = canonical_language(collection["language"])
    return CatalogItem(
        remote_id=remote_id_from_url(public_url),
        collection_id=collection["id"],
        collection_name=collection["name"],
        author_name=author,
        author_key=(
            collection.get("default_author_key") or canonical_author_key(author)
        ),
        language_original=collection["language"],
        language=language,
        language_path=language_path,
        publication_type=canonical_publication_type(
            collection.get("type", ""),
            collection["language"],
        ),
        title_original=title,
        title_normalized=title,
        public_url=public_url,
        assets=tuple(
            sorted(assets, key=lambda item: (item.format != "epub", item.url))
        ),
    )


def re_search_book_url(url: str) -> bool:
    path = urlsplit(url).path.casefold()
    return "/book/" in path or "/read/" in path


def _write_v3_metadata(
    source_root: Path,
    item: CatalogItem,
    state: str,
    sources: list[dict],
    segments: list[dict] | None = None,
    derivations: list[dict] | None = None,
) -> Path:
    identity = item.publication_identity()
    directory = source_root / identity.relative_directory()
    metadata_path = directory / identity.metadata_name()
    history = []
    if metadata_path.is_file():
        try:
            existing = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
            if existing.get("schema_version") == "publication-source/v3":
                history = list(existing.get("history") or [])
        except (OSError, json.JSONDecodeError):
            history = []
    document = build_source_v3(
        item,
        state,
        sources,
        segments=segments,
        derivations=derivations,
        history=history,
    )
    write_json_atomic(metadata_path, document)
    return metadata_path


def preflight_existing_text(
    item: CatalogItem,
    source_root: Path,
) -> tuple[list[Path], Path] | None:
    """Valida Markdown+EPUB derivados sem reescrever nem recolher segmentos."""

    identity = item.publication_identity()
    directory = source_root / identity.relative_directory()
    metadata_path = directory / identity.metadata_name()
    if not metadata_path.is_file():
        return None
    try:
        document = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    if (
        document.get("schema_version") != "publication-source/v3"
        or document.get("state") != "completed"
        or document.get("identity", {}).get("remote_id") != item.remote_id
    ):
        return None
    segment_records = document.get("segments")
    derivations = document.get("derivations")
    if not isinstance(segment_records, list) or not isinstance(derivations, list):
        return None
    if len(segment_records) != len(item.segments):
        return None
    markdown_paths: list[Path] = []
    for expected_order, record in enumerate(segment_records, 1):
        if record.get("order") != expected_order:
            return None
        relative = record.get("path")
        expected_hash = record.get("sha256")
        if not isinstance(relative, str) or not re_full_sha256(expected_hash):
            return None
        path = (directory / relative).resolve()
        if directory.resolve() not in path.parents or not path.is_file():
            return None
        if hash_file(path).sha256 != expected_hash:
            return None
        markdown_paths.append(path)
    epub_records = [
        record
        for record in derivations
        if record.get("format") == "epub"
        and record.get("method") == "local-conversion"
    ]
    if len(epub_records) != 1:
        return None
    epub_record = epub_records[0]
    epub_path = (directory / str(epub_record.get("path", ""))).resolve()
    expected_hash = (epub_record.get("hashes") or {}).get("sha256")
    try:
        if (
            directory.resolve() not in epub_path.parents
            or not epub_path.is_file()
            or not re_full_sha256(expected_hash)
            or hash_file(epub_path).sha256 != expected_hash
        ):
            return None
        validate_generated_epub(epub_path, expected_sections=len(markdown_paths))
    except (OSError, ContractError):
        return None
    return markdown_paths, epub_path


def _process_catalog_item(
    item: CatalogItem,
    source_root: Path,
    session,
    download_config: dict,
    tqdm_factory,
    ledger: AcquisitionLedger,
    *,
    no_network: bool = False,
    revalidate: bool = False,
) -> dict:
    identity = item.publication_identity()
    key = item.stable_key()
    ledger.transition(
        key,
        "processing",
        collection=item.collection_id,
        remote_id=item.remote_id,
        public_url=item.public_url,
    )
    installed_assets: list[Path] = []
    skipped_paths: list[Path] = []
    records: list[dict] = []
    skipped = downloaded = extracted = converted = 0
    try:
        if item.assets:
            for asset in item.assets:
                existing = preflight_existing_asset(
                    asset.url,
                    identity,
                    source_root,
                    remote_asset=asset,
                )
                if existing is not None and not revalidate:
                    records.append(existing[1])
                    skipped_paths.append(existing[0])
                    skipped += 1
                    continue
                if no_network:
                    ledger.transition(key, "pending", reason="network-disabled")
                    return {
                        "state": "pending",
                        "downloaded": 0,
                        "skipped": skipped,
                        "extracted": 0,
                        "converted": 0,
                    }
                target, record, installed = download_asset(
                    session,
                    asset.url,
                    identity,
                    source_root,
                    download_config,
                    tqdm_factory,
                    remote_asset=asset,
                    revalidate=revalidate,
                )
                records.append(record)
                if installed:
                    installed_assets.append(target)
                    downloaded += 1
            if downloaded:
                _write_v3_metadata(source_root, item, "completed", records)
            elif skipped:
                ledger.transition(
                    key,
                    "skipped",
                    reason="already-complete",
                    paths=[
                        str(path.relative_to(REPOSITORY_ROOT))
                        if REPOSITORY_ROOT in path.resolve().parents
                        else str(path)
                        for path in skipped_paths
                    ],
                )
                return {
                    "state": "skipped",
                    "downloaded": 0,
                    "skipped": skipped,
                    "extracted": 0,
                    "converted": 0,
                }
        elif item.segments:
            existing_text = preflight_existing_text(item, source_root)
            if existing_text is not None:
                ledger.transition(
                    key,
                    "skipped",
                    reason="derived-publication-already-complete",
                )
                return {
                    "state": "skipped",
                    "downloaded": 0,
                    "skipped": 1,
                    "extracted": 0,
                    "converted": 0,
                }
            directory = source_root / identity.relative_directory()
            markdown_paths, segment_evidence = write_markdown_publication(
                directory,
                item,
            )
            extracted = len(segment_evidence)
            epub_path = generate_epub(
                directory / identity.asset_name("epub", "derived"),
                item,
                markdown_paths,
            )
            epub_hashes = hash_file(epub_path)
            converted = 1
            segment_sources = [
                {
                    "format": "text",
                    "url": evidence["url"],
                    "method": "text-extraction",
                    "accessed_at": datetime.now(timezone.utc).isoformat(),
                    "size": len(
                        (directory / evidence["path"]).read_bytes()
                    ),
                    "hashes": {"sha256": evidence["sha256"]},
                }
                for evidence in segment_evidence
            ]
            _write_v3_metadata(
                source_root,
                item,
                "completed",
                segment_sources,
                segments=segment_evidence,
                derivations=[
                    {
                        "format": "epub",
                        "method": "local-conversion",
                        "path": epub_path.relative_to(directory).as_posix(),
                        "generator": "egwSearch/FT-006",
                        "source": "text/0000-metadata.json",
                        "hashes": epub_hashes.as_dict(),
                        "size": epub_hashes.size,
                    }
                ],
            )
        else:
            ledger.transition(
                key,
                "review_required",
                reason="no-native-asset-or-verified-segments",
            )
            return {
                "state": "review_required",
                "downloaded": 0,
                "skipped": 0,
                "extracted": 0,
                "converted": 0,
            }
        ledger.transition(
            key,
            "completed",
            downloaded=downloaded,
            skipped=skipped,
            extracted=extracted,
            converted=converted,
        )
        return {
            "state": "completed",
            "downloaded": downloaded,
            "skipped": skipped,
            "extracted": extracted,
            "converted": converted,
        }
    except OriginBlocked:
        ledger.transition(key, "review_required", reason="origin-blocked")
        raise
    except Exception as error:
        for installed_asset in reversed(installed_assets):
            installed_asset.unlink(missing_ok=True)
        ledger.transition(
            key,
            "temporary_failure",
            error=f"{type(error).__name__}:{error}",
        )
        raise


def _process_collection(
    collection: dict,
    config: dict,
    source_root: Path,
    state_root: Path,
    runtime: dict,
    *,
    limit: int | None = None,
    no_network: bool = False,
    fixture_payload: object | None = None,
    shared_limiter: RateLimiter | None = None,
    revalidate: bool = False,
) -> dict:
    """Descobre e processa uma coleção sequencialmente, com parada por bloqueio."""

    download_config = dict(config["download"])
    allowed_catalog_hosts = {
        item.casefold() for item in download_config["allowed_catalog_hosts"]
    }
    _validate_network_url(
        collection["catalog_url"],
        allowed_catalog_hosts,
        require_format=False,
        resolve_dns=not (no_network and fixture_payload is not None),
    )
    limiter = shared_limiter or RateLimiter(_rate_policy(download_config))
    download_config["_rate_limiter"] = limiter
    ledger = AcquisitionLedger(state_root / "ledger.json")
    session = runtime["requests"].Session() if runtime else None
    if session is not None:
        session.headers["User-Agent"] = download_config["user_agent"]
    driver = None
    summary = {
        "collection": collection["id"],
        "discovered": 0,
        "downloaded": 0,
        "skipped": 0,
        "extracted": 0,
        "converted": 0,
        "review_required": 0,
        "failures": 0,
        "blocked": False,
    }
    try:
        if fixture_payload is not None:
            items = parse_catalog_payload(fixture_payload, collection)
        else:
            if no_network:
                raise ContractError("fixture obrigatoria com --no-network")
            options = runtime["FirefoxOptions"]()
            options.add_argument("--headless")
            driver = runtime["webdriver"].Firefox(options=options)
            driver.set_window_size(1920, 1080)
            wait = runtime["WebDriverWait"](driver, 15)
            actions = runtime["ActionChains"](driver)
            limiter.before_request()
            driver.get(collection["catalog_url"])
            page_source = str(driver.page_source or "")
            if contains_block_marker(page_source):
                raise OriginBlocked("desafio anti-automacao no catalogo")
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
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(download_config["delay_seconds"])
                current_height = driver.execute_script(
                    "return document.body.scrollHeight"
                )
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
            items = [
                _catalog_item_from_element(book, collection, runtime)
                for book in books
            ]
        if limit is not None:
            items = items[:limit]
        summary["discovered"] = len(items)
        for index, item in enumerate(items, 1):
            try:
                result = _process_catalog_item(
                    item,
                    source_root,
                    session,
                    download_config,
                    runtime["tqdm"] if runtime else (lambda **_kwargs: _NullProgress()),
                    ledger,
                    no_network=no_network,
                    revalidate=revalidate,
                )
                for key in ("downloaded", "skipped", "extracted", "converted"):
                    summary[key] += result[key]
                if result["state"] == "review_required":
                    summary["review_required"] += 1
                print(
                    f"ITEM_{result['state'].upper()} collection={collection['id']} "
                    f"item={index} remote_id={item.remote_id} "
                    f"title={json.dumps(item.title_original, ensure_ascii=False)}"
                )
            except OriginBlocked as error:
                summary["blocked"] = True
                summary["failures"] += 1
                print(
                    f"COLLECTION_BLOCKED collection={collection['id']} error={error}",
                    file=sys.stderr,
                )
                break
            except Exception as error:
                summary["failures"] += 1
                print(
                    f"ITEM_FAIL collection={collection['id']} item={index} "
                    f"error={type(error).__name__}:{error}",
                    file=sys.stderr,
                )
        return summary
    except OriginBlocked as error:
        summary["blocked"] = True
        summary["failures"] += 1
        print(
            f"COLLECTION_BLOCKED collection={collection['id']} error={error}",
            file=sys.stderr,
        )
        return summary
    finally:
        if session is not None:
            session.close()
        if driver is not None:
            driver.quit()


class _NullProgress:
    def update(self, _size: int) -> None:
        return None

    def close(self) -> None:
        return None


def _selected_collections(config: dict, selected: set[str] | None) -> list[dict]:
    if config["schema_version"] == 2:
        collections = list(config["collections"])
    else:
        collections = [
            {
                **collection,
                "name": collection["id"],
                "default_author_key": author_key,
                "default_author_name": author["name"],
            }
            for author_key, author in config["authors"].items()
            for collection in author["collections"]
        ]
    if not selected:
        return collections
    available = {collection["id"] for collection in collections}
    unknown = selected - available
    if unknown:
        raise ContractError(f"colecao desconhecida: {', '.join(sorted(unknown))}")
    return [collection for collection in collections if collection["id"] in selected]


def _fixture_for_collection(fixture: object, collection_id: str) -> object:
    if isinstance(fixture, dict) and isinstance(fixture.get("collections"), dict):
        collections = fixture["collections"]
        if collection_id not in collections:
            raise ContractError(f"fixture sem colecao: {collection_id}")
        return collections[collection_id]
    return fixture


def run(
    config_path: Path,
    selected: set[str] | None,
    workers: int | None,
    *,
    limit: int | None = None,
    fixture_path: Path | None = None,
    no_network: bool = False,
    revalidate: bool = False,
) -> int:
    config = load_config(config_path)
    source_root = resolve_repository_path(config["source_root"], REPOSITORY_ROOT)
    state_root = resolve_repository_path(
        config.get("state_root", "constructor/.state/publications-acquisition"),
        REPOSITORY_ROOT,
    )
    fixture = None
    if fixture_path is not None:
        try:
            fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ContractError(f"fixture invalida: {fixture_path}: {error}") from error
    runtime = None if fixture is not None and no_network else _runtime_dependencies()
    collections = _selected_collections(config, selected)
    worker_count = workers or config["download"]["workers"]
    maximum_workers = min(
        int(config["download"].get("max_workers", 2)),
        len(collections),
    )
    if worker_count < 1 or worker_count > maximum_workers:
        raise ContractError(f"workers deve estar entre 1 e {maximum_workers}")
    if limit is not None and limit < 1:
        raise ContractError("limit deve ser positivo")
    results = []
    shared_limiter = RateLimiter(_rate_policy(config["download"]))
    if worker_count == 1:
        for collection in collections:
            results.append(
                _process_collection(
                    collection,
                    config,
                    source_root,
                    state_root,
                    runtime,
                    limit=limit,
                    no_network=no_network,
                    fixture_payload=(
                        _fixture_for_collection(fixture, collection["id"])
                        if fixture is not None
                        else None
                    ),
                    shared_limiter=shared_limiter,
                    revalidate=revalidate,
                )
            )
    else:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(
                    _process_collection,
                    collection,
                    config,
                    source_root,
                    state_root,
                    runtime,
                    limit=limit,
                    no_network=no_network,
                    fixture_payload=(
                        _fixture_for_collection(fixture, collection["id"])
                        if fixture is not None
                        else None
                    ),
                    shared_limiter=shared_limiter,
                    revalidate=revalidate,
                ): collection["id"]
                for collection in collections
            }
            for future in as_completed(futures):
                results.append(future.result())
    results.sort(key=lambda item: item["collection"])
    print(json.dumps({"collections": results}, ensure_ascii=False, sort_keys=True))
    return 1 if any(item["failures"] or item["blocked"] for item in results) else 0


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
    parser.add_argument(
        "--limit",
        type=int,
        help="Limite de publicacoes por colecao para amostra controlada.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        help="Catalogo JSON local para validacao deterministica.",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Proibe rede; exige --fixture e processa apenas texto incorporado.",
    )
    parser.add_argument(
        "--revalidate",
        action="store_true",
        help="Usa ETag/Last-Modified persistidos para revalidacao condicional.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        return run(
            Path(arguments.config).resolve(),
            set(arguments.collections) if arguments.collections else None,
            arguments.workers,
            limit=arguments.limit,
            fixture_path=arguments.fixture.resolve() if arguments.fixture else None,
            no_network=arguments.no_network,
            revalidate=arguments.revalidate,
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
