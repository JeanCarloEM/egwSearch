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
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import io
import ipaddress
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
from urllib.parse import urljoin, urlsplit
import re

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
    restore_markdown_from_epub,
    validate_generated_epub,
    write_markdown_publication,
)
from publication_contract import (
    ContractError,
    DEFAULT_CONFIG_PATH,
    REPOSITORY_ROOT,
    build_asset_identity_index,
    build_source_document,
    choose_variant_path,
    format_from_url,
    hash_file,
    load_config,
    publication_identity,
    read_source_records,
    resolve_repository_path,
    runtime_paths,
    uri_slug,
    validate_unique_asset_sha512,
    validate_file_signature,
    validate_source_url,
    write_json_atomic,
)
from publication_transaction import (
    GitPublicationPublisher,
    PublicationTransactionError,
    validate_complete_publication,
)


class DownloadError(RuntimeError):
    """Representa falha conclusiva e sanitizada de aquisicao."""


class NotModified(DownloadError):
    """Resposta condicional confirmou que o ativo remoto não mudou."""


class OfficialCoverMissing(DownloadError):
    """O endpoint oficial comprovou que a capa declarada não existe."""

    def __init__(self, url: str, detail: str, mime: str) -> None:
        super().__init__(f"HTTP 404 em capa oficial: {detail}")
        self.url = url
        self.detail = detail
        self.mime = mime


_metadata_locks: dict[str, threading.Lock] = {}
_metadata_locks_guard = threading.Lock()


def _metadata_lock(path: Path) -> threading.Lock:
    key = str(path.resolve()).casefold()
    with _metadata_locks_guard:
        return _metadata_locks.setdefault(key, threading.Lock())


def _runtime_dependencies() -> dict:
    """Carrega integracoes opcionais sem contaminar importacao do contrato."""

    try:
        import psutil
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
        "psutil": psutil,
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


def _request_cover(session, initial_url: str, download_config: dict):
    """Obtém capa oficial com redirects manuais e a mesma política SSRF dos ativos."""

    allowed_hosts = {item.casefold() for item in download_config["allowed_asset_hosts"]}
    current = initial_url
    limiter = download_config.get("_rate_limiter")
    for redirect_count in range(download_config["max_redirects"] + 1):
        _validate_network_url(current, allowed_hosts, require_format=False)
        response = _get_with_retry(
            session,
            current,
            download_config,
            limiter=limiter,
        )
        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("location")
            response.close()
            if not location or redirect_count == download_config["max_redirects"]:
                raise DownloadError("redirecionamento de capa ausente ou acima do limite")
            current = urljoin(current, location)
            continue
        if response.status_code == 404:
            mime = str(response.headers.get("content-type") or "")
            raw = bytearray()
            try:
                for chunk in response.iter_content(chunk_size=4096):
                    if not chunk:
                        continue
                    raw.extend(chunk)
                    if len(raw) > 16384:
                        break
            finally:
                response.close()
            detail = ""
            if len(raw) <= 16384 and mime.casefold().split(";", 1)[0] in {
                "application/json",
                "application/problem+json",
            }:
                try:
                    problem = json.loads(raw.decode("utf-8"))
                    if isinstance(problem, dict):
                        detail = str(problem.get("detail") or "").strip()
                except (UnicodeDecodeError, json.JSONDecodeError):
                    detail = ""
            if detail == "Cover not found":
                raise OfficialCoverMissing(current, detail, mime)
            raise DownloadError("HTTP 404 não comprova ausência de capa oficial")
        if response.status_code < 200 or response.status_code >= 300:
            response.close()
            raise DownloadError(f"HTTP {response.status_code} em aquisicao de capa")
        return response, current
    raise DownloadError("limite de redirecionamentos de capa excedido")


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
    temporary_root = Path(
        download_config.get("_download_tmp_dir", destination_directory)
    )
    temporary_root.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".download-",
        suffix=f".{publication_format}.partial",
        dir=temporary_root,
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


def validate_cover_png(path: Path, download_config: dict) -> tuple[int, int]:
    """Comprova PNG canônico, dimensões limitadas e ausência de metadado textual."""

    try:
        from PIL import Image

        with Image.open(path) as image:
            image.load()
            if image.format != "PNG":
                raise DownloadError("cover.png nao e PNG")
            width, height = image.size
            maximum = int(download_config.get("cover_max_dimension", 800))
            if width < 1 or height < 1 or width > maximum or height > maximum:
                raise DownloadError("cover.png excede dimensoes permitidas")
            if image.info:
                raise DownloadError("cover.png preservou metadado dispensavel")
            return width, height
    except DownloadError:
        raise
    except Exception as error:
        raise DownloadError("cover.png invalido ou indecodificavel") from error


def _wrap_cover_text(draw, value: str, font, maximum_width: int) -> list[str]:
    """Quebra texto por largura renderizada, preservando resultado determinístico."""

    lines: list[str] = []
    current = ""
    for word in value.split():
        candidate = f"{current} {word}".strip()
        if not current or draw.textbbox((0, 0), candidate, font=font)[2] <= maximum_width:
            current = candidate
            continue
        lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines or [value]


def _technical_cover_text(value: str) -> str:
    """Projeta texto rasterizado para o conjunto seguro da fonte embarcada."""

    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def generate_technical_cover(
    item: CatalogItem,
    source_root: Path,
    download_config: dict,
    missing: OfficialCoverMissing,
) -> tuple[Path, dict, dict]:
    """Gera capa não editorial apenas para ausência oficial conclusiva."""

    from PIL import Image, ImageDraw, ImageFont

    maximum = int(download_config.get("cover_max_dimension", 800))
    height = maximum
    width = max(1, round(maximum * 2 / 3))
    seed = hashlib.sha256(f"egwSearch-cover\0{item.remote_id}".encode("utf-8")).digest()
    background = tuple(24 + (value % 48) for value in seed[:3])
    accent = tuple(150 + (value % 80) for value in seed[3:6])
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    margin = max(24, width // 12)
    title_font = ImageFont.load_default(size=max(28, width // 14))
    author_font = ImageFont.load_default(size=max(18, width // 24))
    label_font = ImageFont.load_default(size=max(14, width // 32))
    draw.rectangle((0, 0, width, max(12, height // 50)), fill=accent)
    label = "CAPA TECNICA NAO EDITORIAL"
    draw.text((margin, height // 9), label, font=label_font, fill=accent)
    y = height // 4
    for line in _wrap_cover_text(
        draw, _technical_cover_text(item.title_normalized), title_font, width - 2 * margin
    ):
        draw.text((margin, y), line, font=title_font, fill=(250, 250, 246))
        y += draw.textbbox((0, 0), line, font=title_font)[3] + max(8, height // 100)
    y = min(max(y + height // 16, height * 2 // 3), height - height // 5)
    for line in _wrap_cover_text(
        draw, _technical_cover_text(item.author_name), author_font, width - 2 * margin
    ):
        draw.text((margin, y), line, font=author_font, fill=(225, 225, 218))
        y += draw.textbbox((0, 0), line, font=author_font)[3] + 6
    footer = f"Capa oficial indisponivel - obra {item.remote_id}"
    draw.text((margin, height - margin * 2), footer, font=label_font, fill=accent)

    directory = source_root / item.publication_identity().relative_directory()
    directory.mkdir(parents=True, exist_ok=True)
    temporary_directory = Path(download_config.get("_download_tmp_dir", directory))
    temporary_directory.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".cover-technical-", suffix=".png.partial", dir=temporary_directory
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        image.save(temporary, format="PNG", optimize=True, compress_level=9)
        validate_cover_png(temporary, download_config)
        target = directory / "cover.png"
        temporary.replace(target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    evidence = hash_file(target)
    accessed_at = datetime.now(timezone.utc).isoformat()
    source_record = {
        "format": "cover",
        "url": item.cover_url,
        "resolved_url": missing.url,
        "method": "official-cover-unavailable",
        "accessed_at": accessed_at,
        "status": 404,
        "detail": missing.detail,
        "mime": missing.mime,
    }
    derivation_record = {
        "format": "cover",
        "method": "deterministic-technical-cover",
        "path": "cover.png",
        "generator": "egwSearch/FT-012",
        "source": item.cover_url,
        "size": evidence.size,
        "hashes": evidence.as_dict(),
    }
    return target, source_record, derivation_record


def download_cover(
    session,
    item: CatalogItem,
    source_root: Path,
    download_config: dict,
) -> tuple[Path, dict, dict]:
    """Adquire a capa declarada e promove um PNG determinístico sem metadados."""

    if not item.cover_url:
        raise ContractError("obra sem URL de capa declarada")
    try:
        response, final_url = _request_cover(session, item.cover_url, download_config)
    except OfficialCoverMissing as missing:
        return generate_technical_cover(item, source_root, download_config, missing)
    maximum_bytes = int(download_config.get("max_cover_bytes", 20 * 1024 * 1024))
    declared_size = response.headers.get("content-length")
    if declared_size:
        try:
            if int(declared_size) > maximum_bytes:
                response.close()
                raise DownloadError("Content-Length da capa acima do limite")
        except ValueError as error:
            response.close()
            raise DownloadError("Content-Length da capa invalido") from error
    raw = bytearray()
    try:
        for chunk in response.iter_content(chunk_size=min(download_config["chunk_bytes"], 262144)):
            if not chunk:
                continue
            raw.extend(chunk)
            if len(raw) > maximum_bytes:
                raise DownloadError("capa excedeu limite de bytes")
    finally:
        response.close()
    if not raw:
        raise DownloadError("capa remota vazia")
    try:
        from PIL import Image, ImageOps

        with Image.open(io.BytesIO(raw)) as opened:
            width, height = opened.size
            if width * height > int(download_config.get("cover_max_pixels", 40_000_000)):
                raise DownloadError("capa excedeu limite de pixels")
            opened.load()
            image = ImageOps.exif_transpose(opened)
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            maximum = int(download_config.get("cover_max_dimension", 800))
            image.thumbnail((maximum, maximum), Image.Resampling.LANCZOS)
            normalized = Image.new(image.mode, image.size)
            normalized.paste(image)
            image = normalized
            directory = source_root / item.publication_identity().relative_directory()
            directory.mkdir(parents=True, exist_ok=True)
            temporary_directory = Path(download_config.get("_download_tmp_dir", directory))
            temporary_directory.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=".cover-",
                suffix=".png.partial",
                dir=temporary_directory,
            )
            os.close(descriptor)
            temporary = Path(temporary_name)
            try:
                image.save(temporary, format="PNG", optimize=True, compress_level=9)
                validate_cover_png(temporary, download_config)
                target = directory / "cover.png"
                temporary.replace(target)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
    except DownloadError:
        raise
    except Exception as error:
        raise DownloadError("capa remota invalida ou indecodificavel") from error
    original_hashes = {
        "sha1": hashlib.sha1(raw, usedforsecurity=False).hexdigest(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "sha512": hashlib.sha512(raw).hexdigest(),
    }
    normalized_hashes = hash_file(target)
    accessed_at = datetime.now(timezone.utc).isoformat()
    source_record = {
        "format": "cover",
        "url": item.cover_url,
        "resolved_url": final_url,
        "method": "official-book-cover",
        "accessed_at": accessed_at,
        "size": len(raw),
        "hashes": original_hashes,
        "mime": response.headers.get("content-type") or "",
    }
    derivation_record = {
        "format": "cover",
        "method": "normalized-official-cover",
        "path": "cover.png",
        "generator": "egwSearch/FT-012",
        "source": item.cover_url,
        "size": normalized_hashes.size,
        "hashes": normalized_hashes.as_dict(),
    }
    return target, source_record, derivation_record


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
        asset_index = download_config.get("_asset_identity_index")
        if isinstance(asset_index, dict):
            candidates = list(
                asset_index.get((publication_format, evidence["sha256"]), [])
            )
            matches = [
                Path(path)
                for path in candidates
                if hash_file(path).sha512 == evidence["sha512"]
            ]
            foreign = [
                path
                for path in matches
                if Path(path).parent.resolve() != destination_directory.resolve()
            ]
            if foreign:
                raise ContractError(
                    "ativo duplicaria publicacao por SHA-512: "
                    + ", ".join(str(path) for path in sorted(foreign))
                )
            if matches:
                temporary.unlink()
                target = Path(sorted(matches)[0])
                installed = False
            else:
                target, duplicate = choose_variant_path(base_path, evidence["sha256"])
                installed = not duplicate
                if duplicate:
                    temporary.unlink()
                else:
                    os.replace(temporary, target)
                    asset_index.setdefault(
                        (publication_format, evidence["sha256"]), []
                    ).append(target.resolve())
        else:
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
    category_name = str(collection.get("category_name") or "").strip()
    category_path = str(collection.get("category") or "").strip()
    if not category_name or not category_path or uri_slug(category_path) != category_path:
        raise ContractError("colecao sem categoria editorial oficial")
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
        category_name=category_name,
        category_path=category_path,
        assets=tuple(
            sorted(assets, key=lambda item: (item.format != "epub", item.url))
        ),
    )


def re_search_book_url(url: str) -> bool:
    path = urlsplit(url).path.casefold()
    return "/book/" in path or "/read/" in path


def _lightweight_public_url(url: str) -> str:
    """Projeta a aplicação pública para a interface textual oficial equivalente."""

    parsed = urlsplit(url)
    if parsed.hostname in {"egwwritings.org", "www.egwwritings.org"}:
        return parsed._replace(netloc="text.egwwritings.org").geturl()
    return url


def _book_id_from_url(url: str) -> str:
    match = re.search(r"/(?:book/b|read/)(\d+)(?:[./]|$)", urlsplit(url).path)
    if not match:
        raise ContractError(f"URL sem identificador de obra: {url}")
    return match.group(1)


def _reader_navigation_url(url: str) -> str:
    """Remove somente variações não editoriais de uma URL de leitura."""

    parsed = urlsplit(_lightweight_public_url(url))
    return parsed._replace(query="", fragment="").geturl()


def _previous_segment_matches(
    segment: CatalogSegment,
    previous_urls: set[str],
) -> bool:
    """Aceita a rota acessada ou o identificador do primeiro bloco da página."""

    if not previous_urls:
        return True
    aliases = {_reader_navigation_url(segment.url)}
    if re.fullmatch(
        rf"{re.escape(_book_id_from_url(segment.url))}\.\d+",
        segment.remote_id,
    ):
        parsed = urlsplit(_reader_navigation_url(segment.url))
        aliases.add(parsed._replace(path=f"/read/{segment.remote_id}").geturl())
    normalized_previous = {_reader_navigation_url(url) for url in previous_urls}
    return bool(aliases.intersection(normalized_previous))


def _clean_catalog_title(value: str) -> str:
    lines = [line.strip() for line in str(value or "").splitlines() if line.strip()]
    if not lines:
        return ""
    return lines[0]


COLLECTION_CHECKPOINT_SCHEMA = "publication-collection-checkpoint/v1"


def _catalog_item_record(item: CatalogItem) -> dict:
    return {
        "remote_id": item.remote_id,
        "collection_id": item.collection_id,
        "collection_name": item.collection_name,
        "author_name": item.author_name,
        "author_key": item.author_key,
        "language_original": item.language_original,
        "language": item.language,
        "language_path": item.language_path,
        "publication_type": item.publication_type,
        "title_original": item.title_original,
        "title_normalized": item.title_normalized,
        "public_url": item.public_url,
        "category_name": item.category_name,
        "category_path": item.category_path,
        "cover_url": item.cover_url,
        "edition": item.edition,
        "assets": [
            {
                "format": asset.format,
                "url": asset.url,
                "etag": asset.etag,
                "last_modified": asset.last_modified,
                "size": asset.size,
                "remote_hash": asset.remote_hash,
            }
            for asset in item.assets
        ],
        "segments": [
            {
                "remote_id": segment.remote_id,
                "url": segment.url,
                "order": segment.order,
                "title": segment.title,
                "html": segment.html,
            }
            for segment in item.segments
        ],
        "local_complete": item.local_complete,
    }


def _catalog_item_from_record(value: object) -> CatalogItem:
    if not isinstance(value, dict):
        raise ContractError("item inválido no checkpoint de coleção")
    try:
        assets = tuple(CatalogAsset(**asset) for asset in value.get("assets", []))
        segments = tuple(CatalogSegment(**segment) for segment in value.get("segments", []))
        return CatalogItem(
            remote_id=str(value["remote_id"]),
            collection_id=str(value["collection_id"]),
            collection_name=str(value["collection_name"]),
            author_name=str(value["author_name"]),
            author_key=str(value["author_key"]),
            language_original=str(value["language_original"]),
            language=str(value["language"]),
            language_path=str(value["language_path"]),
            publication_type=str(value["publication_type"]),
            title_original=str(value["title_original"]),
            title_normalized=str(value["title_normalized"]),
            public_url=str(value["public_url"]),
            category_name=str(value["category_name"]),
            category_path=str(value["category_path"]),
            cover_url=str(value.get("cover_url") or ""),
            edition=str(value.get("edition") or ""),
            assets=assets,
            segments=segments,
            local_complete=bool(value.get("local_complete", False)),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ContractError("item inválido no checkpoint de coleção") from error


def _collection_checkpoint_path(
    state_root: Path,
    collection: dict,
    limit: int | None,
    publication_query: str | None,
) -> Path:
    scope = json.dumps(
        {
            "collection": collection["id"],
            "limit": limit,
            "publication_query": (publication_query or "").casefold().strip(),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    suffix = hashlib.sha256(scope.encode("utf-8")).hexdigest()[:16]
    return state_root / "collections" / uri_slug(collection["id"]) / f"{suffix}.json"


def _new_collection_checkpoint(
    collection: dict,
    limit: int | None,
    publication_query: str | None,
) -> dict:
    return {
        "schema_version": COLLECTION_CHECKPOINT_SCHEMA,
        "collection_id": collection["id"],
        "catalog_url": _lightweight_public_url(collection["catalog_url"]),
        "limit": limit,
        "publication_query": (publication_query or "").casefold().strip(),
        "catalog_entries": [],
        "items": [],
        "confirmed_remote_ids": [],
        "discovery_complete": False,
    }


def _load_collection_checkpoint(
    path: Path,
    collection: dict,
    limit: int | None,
    publication_query: str | None,
) -> dict | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(
            f"checkpoint de coleção inválido; use --restart: {path}"
        ) from error
    expected = _new_collection_checkpoint(collection, limit, publication_query)
    if not isinstance(value, dict) or any(
        value.get(key) != expected[key]
        for key in (
            "schema_version",
            "collection_id",
            "catalog_url",
            "limit",
            "publication_query",
        )
    ):
        raise ContractError(f"checkpoint de coleção incompatível; use --restart: {path}")
    entries = value.get("catalog_entries")
    items = value.get("items")
    confirmed = value.get("confirmed_remote_ids")
    if (
        not isinstance(entries, list)
        or not isinstance(items, list)
        or not isinstance(confirmed, list)
        or not isinstance(value.get("discovery_complete"), bool)
        or len(items) > len(entries)
        or (value.get("discovery_complete") and len(items) != len(entries))
        or any(
            not isinstance(entry, dict)
            or set(entry) != {"title", "url", "author"}
            or not all(isinstance(entry[key], str) for key in entry)
            for entry in entries
        )
        or any(not isinstance(remote_id, str) or not remote_id for remote_id in confirmed)
    ):
        raise ContractError(f"checkpoint de coleção corrompido; use --restart: {path}")
    parsed_items = [_catalog_item_from_record(item) for item in items]
    remote_ids = [item.remote_id for item in parsed_items]
    try:
        mapping_invalid = any(
            item.collection_id != collection["id"]
            or item.remote_id != _book_id_from_url(entries[index]["url"])
            for index, item in enumerate(parsed_items)
        )
    except ContractError:
        mapping_invalid = True
    if (
        len(remote_ids) != len(set(remote_ids))
        or len(confirmed) != len(set(confirmed))
        or not set(confirmed).issubset(set(remote_ids))
        or mapping_invalid
    ):
        raise ContractError(f"checkpoint de coleção ambíguo; use --restart: {path}")
    value["_items"] = parsed_items
    return value


def _save_collection_checkpoint(path: Path, checkpoint: dict) -> None:
    write_json_atomic(
        path,
        {key: value for key, value in checkpoint.items() if not key.startswith("_")},
    )


class BrowserSessionManager:
    """Mantem uma unica sessao/guia Selenium visivel para descoberta remota."""

    def __init__(self, runtime: dict, download_config: dict, paths: dict[str, Path]) -> None:
        self.runtime = runtime
        self.config = dict(download_config)
        self.state_root = Path(paths["root"])
        self.profile_dir = Path(paths["browser_profile"])
        self.visible = bool(self.config.get("browser_visible", True))
        self.handoff_enabled = bool(self.config.get("browser_handoff_enabled", True))
        self.wait_interval = max(
            1.0,
            float(self.config.get("browser_wait_interval_seconds", 5.0)),
        )
        self.human_wait_limit = max(
            0.0,
            float(self.config.get("browser_human_wait_seconds", 0.0)),
        )
        self.catalog_wait = max(
            self.wait_interval,
            float(self.config.get("browser_catalog_wait_seconds", 30.0)),
        )
        self.recovery_limit = max(
            0,
            int(self.config.get("browser_recovery_limit", 2)),
        )
        self._driver = None
        self._primary_handle = None
        self._recoveries = 0
        self._handoffs = 0
        self._profile_resets = 0

    def close(self) -> None:
        if self._driver is None:
            return
        try:
            self._driver.quit()
            print("BROWSER_SESSION_CLOSED")
        finally:
            self._driver = None
            self._primary_handle = None

    def discover_catalog_items(
        self,
        collection: dict,
        limiter: RateLimiter,
        limit: int | None = None,
        publication_query: str | None = None,
        local_preflight=None,
        checkpoint_path: Path | None = None,
        checkpoint: dict | None = None,
        restart: bool = False,
    ) -> list[CatalogItem]:
        """Enumera todas as obras e as enriquece pela página individual."""

        active = checkpoint or _new_collection_checkpoint(
            collection, limit, publication_query
        )
        stored_entries = active.get("catalog_entries") or []
        items = list(active.get("_items") or [])
        if stored_entries:
            ordered = [
                (entry["title"], entry["url"], entry["author"])
                for entry in stored_entries
            ]
            print(
                f"CATALOG_DISCOVERY_RESUME collection={collection['id']} "
                f"enriched={len(items)} publications={len(ordered)}"
            )
        else:
            driver = self._usable_driver()
            limiter.before_request()
            print(
                f"BROWSER_TAB_REUSE collection={collection['id']} "
                f"profile={self._safe_profile_label()}"
            )
            catalog_url = _lightweight_public_url(collection["catalog_url"])
            driver.get(catalog_url)
            driver = self._wait_for_human_release(collection["id"])
            if urlsplit(catalog_url).hostname != "text.egwwritings.org":
                self._accept_cookie_banner()
            links = self._discover_catalog_links(collection, limiter)
            if not links:
                # Compatibilidade com a aplicação completa e fixtures Selenium
                # antigas, sem checkpoint incremental para DOM virtualizado.
                virtualized: dict[str, CatalogItem] = {}
                self._harvest_virtualized_cards(collection, virtualized)
                self._scroll_until_stable(
                    on_step=lambda: self._harvest_virtualized_cards(
                        collection, virtualized
                    )
                )
                self._wait_for_catalog_grid(collection["id"])
                self._harvest_virtualized_cards(collection, virtualized)
                values = sorted(
                    virtualized.values(),
                    key=lambda item: item.title_normalized.casefold(),
                )
                values = values[:limit] if limit is not None else values
                if checkpoint_path is None:
                    return values
                active["catalog_entries"] = [
                    {
                        "title": item.title_original,
                        "url": item.public_url,
                        "author": item.author_name,
                    }
                    for item in values
                ]
                active["items"] = [_catalog_item_record(item) for item in values]
                active["_items"] = values
                active["discovery_complete"] = True
                if checkpoint_path is not None:
                    _save_collection_checkpoint(checkpoint_path, active)
                return values
            print(
                f"CATALOG_DISCOVERED collection={collection['id']} "
                f"publications={len(links)} source=lightweight-public"
            )
            ordered = sorted(links.values(), key=lambda value: value[0].casefold())
            if publication_query:
                query = publication_query.casefold().strip()
                ordered = [
                    value
                    for value in ordered
                    if query in value[0].casefold()
                    or query in value[1].casefold()
                    or query == _book_id_from_url(value[1])
                ]
                if not ordered:
                    raise ContractError(
                        f"publicação não encontrada na coleção: {publication_query}"
                    )
            if limit is not None:
                ordered = ordered[:limit]
            active["catalog_entries"] = [
                {"title": title, "url": url, "author": author}
                for title, url, author in ordered
            ]
            if checkpoint_path is not None:
                _save_collection_checkpoint(checkpoint_path, active)

        if active.get("discovery_complete"):
            if len(items) != len(ordered):
                raise ContractError("checkpoint concluído com catálogo parcial; use --restart")
            return items

        for title, url, author in ordered[len(items) :]:
            remote_id = _book_id_from_url(url)
            if restart:
                self._text_checkpoint_path(remote_id).unlink(missing_ok=True)
            local = (
                local_preflight(remote_id, title, url, author)
                if local_preflight
                else None
            )
            if local is not None:
                items.append(local)
                print(
                    f"PUBLICATION_LOCAL_VALID remote_id={remote_id} "
                    "network=skipped"
                )
            else:
                items.append(
                    self._enrich_book(
                        collection,
                        url,
                        title,
                        author,
                        limiter,
                        restart=restart,
                    )
                )
            active["items"] = [_catalog_item_record(item) for item in items]
            active["_items"] = items
            if checkpoint_path is not None:
                _save_collection_checkpoint(checkpoint_path, active)
        active["discovery_complete"] = True
        active["items"] = [_catalog_item_record(item) for item in items]
        active["_items"] = items
        if checkpoint_path is not None:
            _save_collection_checkpoint(checkpoint_path, active)
        return items

    def _text_checkpoint_path(self, book_id: str) -> Path:
        return self.state_root / "acquisition" / "text" / f"{book_id}.json"

    def _discover_catalog_links(
        self,
        collection: dict,
        limiter: RateLimiter,
    ) -> dict[str, tuple[str, str, str]]:
        """Coleta links estáticos de obra e, nas pioneiras, catálogos autorais."""

        driver = self._usable_driver()
        by = self.runtime["By"]
        result: dict[str, tuple[str, str, str]] = {}

        def harvest(author: str = "") -> None:
            for link in driver.find_elements(by.CSS_SELECTOR, "a[href*='/book/']"):
                href = str(link.get_attribute("href") or "").strip()
                title = _clean_catalog_title(link.text)
                if not href or not title:
                    continue
                absolute = _lightweight_public_url(urljoin(str(driver.current_url), href))
                result.setdefault(absolute, (title, absolute, author))

        harvest(str(collection.get("default_author_name") or "").strip())
        if result or not collection.get("discover_authors"):
            return result

        language_code = "pt" if canonical_language(collection["language"])[0] == "pt-BR" else "en"
        author_links: dict[str, str] = {}
        selector = f"a[href*='/allCollection/{language_code}/']"
        for link in driver.find_elements(by.CSS_SELECTOR, selector):
            href = str(link.get_attribute("href") or "").strip()
            author = _clean_catalog_title(link.text)
            absolute = _lightweight_public_url(urljoin(str(driver.current_url), href))
            path = urlsplit(absolute).path.rstrip("/")
            if not author or not re.fullmatch(rf"/allCollection/{language_code}/\d+", path):
                continue
            if absolute != _lightweight_public_url(collection["catalog_url"]):
                author_links[absolute] = author
        for author_url, author in sorted(author_links.items()):
            limiter.before_request()
            driver.get(author_url)
            self._wait_for_human_release(f"{collection['id']}:{author}")
            harvest(author)
        return result

    def _enrich_book(
        self,
        collection: dict,
        public_url: str,
        title_candidate: str,
        author_candidate: str,
        limiter: RateLimiter,
        restart: bool = False,
    ) -> CatalogItem:
        """Usa a página da obra como autoridade de identidade, ativos e leitura."""

        driver = self._usable_driver()
        limiter.before_request()
        driver.get(_lightweight_public_url(public_url))
        self._wait_for_human_release(f"book:{_book_id_from_url(public_url)}")
        title = _first_element_text(
            driver,
            self.runtime,
            [".breadcrumbs-header-title", ".book-info h1", "main h1"],
        ) or title_candidate
        author = _first_element_text(
            driver,
            self.runtime,
            [".book-info-content__subtitle__author", "[class*='author']"],
        ) or author_candidate or str(collection.get("default_author_name") or "")
        author = re.sub(r"^\s*By[\s\u00a0]+", "", author, flags=re.IGNORECASE).strip()
        if not title or not author:
            raise ContractError("página individual sem título ou autor comprovado")
        cover_url = ""
        for selector in (
            "meta[property='og:image']",
            "meta[name='twitter:image']",
            "meta[property='twitter:image']",
        ):
            elements = driver.find_elements(self.runtime["By"].CSS_SELECTOR, selector)
            if not elements:
                continue
            candidate = str(elements[0].get_attribute("content") or "").strip()
            if candidate:
                cover_url = urljoin(str(driver.current_url), candidate)
                break
        assets: dict[tuple[str, str], CatalogAsset] = {}
        read_url = ""
        for link in driver.find_elements(self.runtime["By"].TAG_NAME, "a"):
            href = str(link.get_attribute("href") or "").strip()
            disabled = link.get_attribute("disabled") is not None
            if not href or href == "#" or disabled:
                continue
            absolute = urljoin(str(driver.current_url), href)
            try:
                publication_format = format_from_url(absolute)
            except ContractError:
                if "/read/" in urlsplit(absolute).path and not read_url:
                    read_url = _lightweight_public_url(absolute)
                continue
            assets[(publication_format, absolute)] = CatalogAsset(
                format=publication_format,
                url=absolute,
            )
        language, language_path = canonical_language(collection["language"])
        category_name = str(collection.get("category_name") or "").strip()
        category_path = str(collection.get("category") or "").strip()
        if not category_name or not category_path or uri_slug(category_path) != category_path:
            raise ContractError("colecao sem categoria editorial oficial")
        segments: tuple[CatalogSegment, ...] = ()
        if not assets:
            if not read_url:
                raise ContractError("obra sem ativo nativo e sem URL Read Online")
            segments = tuple(
                self._discover_text_segments(read_url, limiter, restart=restart)
            )
        canonical_url = _lightweight_public_url(public_url)
        return CatalogItem(
            remote_id=remote_id_from_url(canonical_url),
            collection_id=collection["id"],
            collection_name=collection["name"],
            author_name=author,
            author_key=collection.get("default_author_key") or canonical_author_key(author),
            language_original=collection["language"],
            language=language,
            language_path=language_path,
            publication_type=canonical_publication_type(
                collection.get("type", ""), collection["language"]
            ),
            title_original=title,
            title_normalized=title,
            public_url=canonical_url,
            category_name=category_name,
            category_path=category_path,
            cover_url=cover_url,
            assets=tuple(sorted(assets.values(), key=lambda item: (item.format != "epub", item.url))),
            segments=segments,
        )

    def _discover_text_segments(
        self,
        initial_url: str,
        limiter: RateLimiter,
        *,
        restart: bool = False,
    ) -> list[CatalogSegment]:
        """Percorre a cadeia editorial real `rel=next` sem saltar páginas."""

        book_id = _book_id_from_url(initial_url)
        current = _lightweight_public_url(initial_url)
        visited: set[str] = set()
        segments: list[CatalogSegment] = []
        checkpoint_path = self._text_checkpoint_path(book_id)
        if restart:
            checkpoint_path.unlink(missing_ok=True)
        if checkpoint_path.is_file():
            try:
                checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
                if (
                    checkpoint.get("schema_version") != "publication-text-checkpoint/v1"
                    or checkpoint.get("initial_url") != current
                    or not isinstance(checkpoint.get("segments"), list)
                ):
                    raise ContractError("checkpoint textual incompatível; use --restart")
                segments = [
                    CatalogSegment(
                        remote_id=str(value["remote_id"]),
                        url=str(value["url"]),
                        order=int(value["order"]),
                        title=str(value["title"]),
                        html=str(value["html"]),
                    )
                    for value in checkpoint["segments"]
                ]
                visited = {segment.url for segment in segments}
                current = str(checkpoint.get("next_url") or "")
                if checkpoint.get("complete"):
                    return segments
                print(
                    f"TEXT_DISCOVERY_RESUME book={book_id} units={len(segments)}"
                )
            except ContractError:
                raise
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
                raise ContractError(
                    f"checkpoint textual inválido; use --restart: {checkpoint_path}"
                ) from error
        driver = self._usable_driver()
        by = self.runtime["By"]
        while current:
            if len(segments) >= 10000:
                raise ContractError("cadeia editorial excedeu o limite seguro")
            normalized = current.split("#", 1)[0]
            if normalized in visited:
                raise ContractError("ciclo na navegação editorial")
            if _book_id_from_url(normalized) != book_id:
                raise ContractError("navegação editorial mudou de obra")
            visited.add(normalized)
            limiter.before_request()
            driver.get(normalized)
            self._wait_for_human_release(f"read:{book_id}:{len(segments) + 1}")
            containers = driver.find_elements(by.CSS_SELECTOR, "#r-pl")
            if len(containers) != 1:
                raise ContractError("página de leitura sem contêiner editorial único")
            payload = driver.execute_script(
                """
                const source = document.querySelector('#r-pl');
                if (!source) return null;
                const copy = source.cloneNode(true);
                copy.querySelectorAll('.refCode,.anchor-link,script,style,button,nav,aside').forEach((e) => e.remove());
                const first = copy.querySelector('[id]');
                const heading = copy.querySelector('h1,h2,h3,h4,h5,h6,.h1,.h2,.h3,.h4,.h5,.h6');
                return {html: copy.innerHTML, firstId: first ? first.id : '', title: heading ? heading.textContent.trim() : ''};
                """
            )
            if not isinstance(payload, dict) or not str(payload.get("html") or "").strip():
                raise ContractError("página de leitura sem conteúdo editorial real")
            first_id = str(payload.get("firstId") or "").strip()
            segment_id = first_id or urlsplit(normalized).path.rsplit("/", 1)[-1]
            title = str(payload.get("title") or "").strip() or f"Unidade {len(segments) + 1}"
            segments.append(
                CatalogSegment(
                    remote_id=segment_id,
                    url=normalized,
                    order=len(segments) + 1,
                    title=title,
                    html=f'<section data-source-id="{segment_id}">{payload["html"]}</section>',
                )
            )
            prev_links = driver.find_elements(by.CSS_SELECTOR, "#reader a[rel='prev']")
            prev_urls = {
                urljoin(normalized, str(link.get_attribute("href") or "")).split("#", 1)[0]
                for link in prev_links
                if link.get_attribute("disabled") is None and link.get_attribute("href")
            }
            if len(segments) > 1 and not _previous_segment_matches(
                segments[-2], prev_urls
            ):
                raise ContractError("navegação editorial anterior/próximo divergente")
            next_links = driver.find_elements(by.CSS_SELECTOR, "#reader a[rel='next']")
            next_urls = {
                urljoin(normalized, str(link.get_attribute("href") or "")).split("#", 1)[0]
                for link in next_links
                if link.get_attribute("disabled") is None and link.get_attribute("href") not in {None, "", "#"}
            }
            if len(next_urls) > 1:
                raise ContractError("página de leitura com próximos divergentes")
            current = next(iter(next_urls)) if next_urls else ""
            write_json_atomic(
                checkpoint_path,
                {
                    "schema_version": "publication-text-checkpoint/v1",
                    "initial_url": _lightweight_public_url(initial_url),
                    "next_url": current,
                    "complete": not bool(current),
                    "segments": [
                        {
                            "remote_id": segment.remote_id,
                            "url": segment.url,
                            "order": segment.order,
                            "title": segment.title,
                            "html": segment.html,
                        }
                        for segment in segments
                    ],
                },
            )
            if len(segments) == 1 or len(segments) % 10 == 0 or not current:
                print(
                    f"TEXT_DISCOVERY_PROGRESS book={book_id} "
                    f"units={len(segments)} complete={str(not bool(current)).lower()}"
                )
        if not segments:
            raise ContractError("obra textual sem segmentos")
        return segments

    def _harvest_virtualized_cards(
        self,
        collection: dict,
        items: dict[str, CatalogItem],
    ) -> None:
        driver = self._usable_driver()
        for book in driver.find_elements(self.runtime["By"].CLASS_NAME, "book-list-item"):
            try:
                item = _catalog_item_from_element(book, collection, self.runtime)
            except ContractError:
                continue
            items.setdefault(item.stable_key(), item)

    def _safe_profile_label(self) -> str:
        try:
            return self.profile_dir.relative_to(REPOSITORY_ROOT).as_posix()
        except ValueError:
            return "<perfil-segregado>"

    def _usable_driver(self):
        if self._driver is None:
            return self._launch_driver("create")
        try:
            handles = list(self._driver.window_handles)
        except Exception:
            return self._recover_driver("navegador encerrado")
        if not handles:
            return self._recover_driver("guia operacional fechada")
        if self._primary_handle not in handles:
            return self._recover_driver("guia operacional invalida")
        self._driver.switch_to.window(self._primary_handle)
        return self._driver

    def _launch_driver(self, action: str):
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self._quarantine_stale_browser_markers()
        options = self.runtime["FirefoxOptions"]()
        if self.visible:
            options.add_argument("-profile")
            options.add_argument(str(self.profile_dir))
        else:
            options.add_argument("--headless")
            options.add_argument("-profile")
            options.add_argument(str(self.profile_dir))
        try:
            driver = self.runtime["webdriver"].Firefox(options=options)
        except Exception as error:
            if action != "create" or self._profile_resets >= 1:
                raise DownloadError(
                    f"Firefox não iniciou sessão controlada: {type(error).__name__}"
                ) from error
            self._quarantine_corrupted_profile(type(error).__name__)
            return self._launch_driver(action)
        try:
            driver.set_window_size(
                int(self.config.get("browser_window_width", 1920)),
                int(self.config.get("browser_window_height", 1080)),
            )
        except Exception:
            pass
        handles = list(driver.window_handles)
        if not handles:
            driver.quit()
            raise DownloadError("navegador sem guia operacional")
        self._driver = driver
        self._primary_handle = handles[0]
        print(
            f"BROWSER_SESSION_{action.upper()} visible={str(self.visible).lower()} "
            f"profile={self._safe_profile_label()} tabs=1"
        )
        return driver

    def _quarantine_corrupted_profile(self, reason: str) -> None:
        """Preserva perfil inutilizável e permite uma única recriação limpa."""

        binary = self._human_browser_binary()
        if self._browser_process_ids(binary):
            raise DownloadError(
                "perfil não pode ser recuperado enquanto houver Firefox ativo"
            )
        self._profile_resets += 1
        if self.profile_dir.exists():
            quarantine = self.state_root / "profiles-quarantine"
            quarantine.mkdir(parents=True, exist_ok=True)
            target = quarantine / (
                f"{self.profile_dir.name}.{time.time_ns()}.corrupted"
            )
            try:
                self.profile_dir.replace(target)
            except OSError as error:
                raise DownloadError("falha ao preservar perfil corrompido") from error
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        print(
            f"BROWSER_PROFILE_RESET reason={json.dumps(reason)} preserved=true",
            file=sys.stderr,
        )

    def _quarantine_stale_browser_markers(self) -> None:
        """Preserva resíduos renomeáveis e bloqueia perfil efetivamente ativo."""

        names = ("parent.lock", ".parentlock", "lock", "MarionetteActivePort")
        markers = [self.profile_dir / name for name in names]
        markers = [path for path in markers if path.exists() or path.is_symlink()]
        if not markers:
            return
        if os.name != "nt":
            raise DownloadError("perfil possui marcador de uso; confirme Firefox encerrado")
        quarantine = self.state_root / "tmp" / "obsolete-browser-markers"
        quarantine.mkdir(parents=True, exist_ok=True)
        moved: list[tuple[Path, Path]] = []
        try:
            for marker in markers:
                target = quarantine / f"{marker.name}.{time.time_ns()}.stale"
                marker.replace(target)
                moved.append((marker, target))
        except OSError as error:
            for original, preserved in reversed(moved):
                preserved.replace(original)
            raise DownloadError(
                "perfil do Firefox está em uso; encerre a sessão antes de continuar"
            ) from error

    def _recover_driver(self, reason: str):
        if self._recoveries >= self.recovery_limit:
            raise DownloadError(
                f"recuperacao do navegador excedeu limite: {reason}"
            )
        self._recoveries += 1
        print(
            f"BROWSER_SESSION_RECOVERY attempt={self._recoveries} "
            f"reason={json.dumps(reason, ensure_ascii=False)}",
            file=sys.stderr,
        )
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
        self._driver = None
        self._primary_handle = None
        return self._launch_driver("recover")

    def _accept_cookie_banner(self) -> None:
        driver = self._usable_driver()
        try:
            wait = self.runtime["WebDriverWait"](
                driver,
                self.catalog_wait,
                poll_frequency=self.wait_interval,
            )
            cookie = wait.until(
                self.runtime["EC"].presence_of_element_located(
                    (
                        self.runtime["By"].CSS_SELECTOR,
                        "div[class^='Ripple_root__lmfsr Ripple_dark__']",
                    )
                )
            )
            self.runtime["ActionChains"](driver).move_to_element(cookie).click().perform()
        except Exception:
            pass

    def _scroll_until_stable(self, on_step=None) -> None:
        driver = self._usable_driver()
        last_height = driver.execute_script("return document.body.scrollHeight")
        stable = 0
        while stable < 3:
            driver = self._wait_for_human_release("scroll")
            if on_step is not None:
                on_step()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(float(self.config["delay_seconds"]))
            current_height = driver.execute_script("return document.body.scrollHeight")
            stable = stable + 1 if current_height == last_height else 0
            last_height = current_height
        if on_step is not None:
            on_step()

    def _wait_for_catalog_grid(self, collection_id: str) -> None:
        while True:
            driver = self._usable_driver()
            driver = self._wait_for_human_release(collection_id)
            try:
                wait = self.runtime["WebDriverWait"](
                    driver,
                    self.catalog_wait,
                    poll_frequency=self.wait_interval,
                )
                wait.until(
                    self.runtime["EC"].presence_of_element_located(
                        (
                            self.runtime["By"].CLASS_NAME,
                            "ReactVirtualized__Grid__innerScrollContainer",
                        )
                    )
                )
                return
            except Exception as error:
                if self._challenge_detected(driver):
                    continue
                raise DownloadError(
                    f"catalogo sem grade esperada: {collection_id}"
                ) from error

    def _wait_for_human_release(self, scope: str):
        driver = self._usable_driver()
        if not self._challenge_detected(driver):
            return driver
        self._handoff_to_human(scope, str(driver.current_url or ""))
        resumed = self._launch_driver("resume")
        resumed.get(self._handoff_url)
        if self._challenge_detected(resumed):
            raise OriginBlocked(
                "sessão humana encerrada, mas o desafio permanece; estado preservado"
            )
        expected = urlsplit(self._handoff_url)
        current = urlsplit(str(resumed.current_url or ""))
        if current.scheme != expected.scheme or current.hostname != expected.hostname:
            raise OriginBlocked(
                "sessão humana retomou em origem divergente; estado preservado"
            )
        print(f"HUMAN_VERIFICATION_RELEASED scope={scope}")
        return resumed

    def _human_browser_binary(self) -> str:
        configured = str(self.config.get("browser_human_binary", "")).strip()
        candidates = [configured] if configured else []
        discovered = shutil.which("firefox")
        if discovered:
            candidates.append(discovered)
        if os.name == "nt":
            for variable in ("ProgramFiles", "ProgramFiles(x86)"):
                root = os.environ.get(variable)
                if root:
                    candidates.append(str(Path(root) / "Mozilla Firefox" / "firefox.exe"))
        for candidate in candidates:
            path = Path(candidate).expanduser()
            if path.is_file():
                return str(path.resolve())
        raise OriginBlocked(
            "Firefox normal não encontrado; configure browser_human_binary"
        )

    def _handoff_to_human(self, scope: str, url: str) -> None:
        """Encerra o WebDriver antes de entregar o perfil ao navegador normal."""

        if not self.visible or not self.handoff_enabled:
            raise OriginBlocked("handoff humano desabilitado ou navegador não visível")
        if self._handoffs >= self.recovery_limit + 1:
            raise OriginBlocked("limite de handoffs humanos excedido")
        self._handoffs += 1
        self._handoff_url = url
        started = time.monotonic()
        self.close()
        binary = self._human_browser_binary()
        baseline_pids = self._browser_process_ids(binary)
        print(
            f"HUMAN_HANDOFF_STARTED scope={scope} method=detached-browser",
            file=sys.stderr,
        )
        print(
            "A automação foi encerrada. Resolva a verificação no Firefox normal e "
            "feche essa janela para validar a retomada; Ctrl+C cancela com segurança.",
            file=sys.stderr,
        )
        process = subprocess.Popen(
            [
                binary,
                "-no-remote",
                "-profile",
                str(self.profile_dir),
                url,
            ],
            cwd=REPOSITORY_ROOT,
        )
        observed_browser_process = False
        launcher_finished_at: float | None = None
        while True:
            return_code = process.poll()
            active_pids = self._browser_process_ids(binary) - baseline_pids
            observed_browser_process = observed_browser_process or bool(active_pids)
            if return_code is not None and launcher_finished_at is None:
                launcher_finished_at = time.monotonic()
            if return_code is not None and not active_pids:
                grace_elapsed = time.monotonic() - launcher_finished_at
                if observed_browser_process or grace_elapsed >= max(2.0, self.wait_interval * 2):
                    break
            if self.human_wait_limit and time.monotonic() - started >= self.human_wait_limit:
                self._terminate_browser_processes(active_pids)
                if return_code is None:
                    process.terminate()
                raise OriginBlocked(
                    "tempo de intervenção humana excedido; feche o Firefox normal"
                )
            time.sleep(self.wait_interval)
        if process.returncode not in {0, None}:
            raise OriginBlocked(
                f"navegador humano encerrou com código {process.returncode}"
            )
        print(
            f"HUMAN_HANDOFF_FINISHED scope={scope} seconds={int(time.monotonic() - started)}",
            file=sys.stderr,
        )

    def _browser_process_ids(self, binary: str) -> set[int]:
        expected = Path(binary).resolve()
        result: set[int] = set()
        for process in self.runtime["psutil"].process_iter(["pid", "exe"]):
            try:
                executable = process.info.get("exe")
                if executable and Path(executable).resolve() == expected:
                    result.add(int(process.info["pid"]))
            except (OSError, self.runtime["psutil"].Error):
                continue
        return result

    def _terminate_browser_processes(self, process_ids: set[int]) -> None:
        processes = []
        for process_id in sorted(process_ids, reverse=True):
            try:
                process = self.runtime["psutil"].Process(process_id)
                process.terminate()
                processes.append(process)
            except self.runtime["psutil"].Error:
                continue
        if processes:
            _gone, alive = self.runtime["psutil"].wait_procs(processes, timeout=10)
            for process in alive:
                try:
                    process.kill()
                except self.runtime["psutil"].Error:
                    pass

    def _challenge_detected(self, driver) -> bool:
        try:
            material = "\n".join(
                (
                    str(driver.title or ""),
                    str(driver.current_url or ""),
                    str(driver.page_source or ""),
                )
            )
        except Exception:
            self._recover_driver("falha ao inspecionar guia operacional")
            return False
        return contains_block_marker(material)


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
    download_config: dict,
) -> tuple[Path, Path | None] | None:
    """Valida EPUB, fonte Markdown interna e capa sem depender de `.md` externo."""

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
    cover_path: Path | None = None
    cover_hash = ""
    if item.cover_url:
        cover_sources = [
            record
            for record in document.get("sources", [])
            if record.get("format") == "cover" and record.get("url") == item.cover_url
        ]
        cover_derivations = [
            record
            for record in derivations
            if record.get("format") == "cover"
            and record.get("method")
            in {"normalized-official-cover", "deterministic-technical-cover"}
        ]
        if len(cover_sources) != 1 or len(cover_derivations) != 1:
            return None
        cover_source = cover_sources[0]
        cover_record = cover_derivations[0]
        expected_pair = {
            "normalized-official-cover": "official-book-cover",
            "deterministic-technical-cover": "official-cover-unavailable",
        }
        if expected_pair.get(cover_record.get("method")) != cover_source.get("method"):
            return None
        cover_path = (directory / str(cover_record.get("path", ""))).resolve()
        cover_hash = (cover_record.get("hashes") or {}).get("sha256", "")
        try:
            if (
                directory.resolve() not in cover_path.parents
                or cover_path.name != "cover.png"
                or not cover_path.is_file()
                or not re_full_sha256(cover_hash)
                or hash_file(cover_path).sha256 != cover_hash
            ):
                return None
            validate_cover_png(cover_path, download_config)
        except (OSError, DownloadError):
            return None
    if len(segment_records) != len(item.segments):
        return None
    expected_markdown: dict[str, str] = {}
    for expected_order, record in enumerate(segment_records, 1):
        if record.get("order") != expected_order:
            return None
        relative = record.get("path")
        expected_hash = record.get("sha256")
        if not isinstance(relative, str) or not re_full_sha256(expected_hash):
            return None
        prefix = f"{identity.asset_name('epub', 'derived')}!/META-INF/egwsearch-source/"
        if not relative.startswith(prefix):
            return None
        name = relative.removeprefix(prefix)
        if Path(name).name != name or not name.endswith(".md") or name in expected_markdown:
            return None
        expected_markdown[name] = expected_hash
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
        validate_generated_epub(
            epub_path,
            expected_sections=len(segment_records),
            expected_cover_sha256=(cover_hash or None),
            expected_markdown_sha256=expected_markdown,
            expected_public_url=item.public_url,
            expected_accessed_at=str(epub_record.get("accessed_at") or ""),
        )
    except (OSError, ContractError, ValueError):
        return None
    return epub_path, cover_path


def build_local_publication_index(source_root: Path) -> dict[str, list[Path]]:
    """Indexa metadados locais por ID remoto sem confiar neles antes da validação."""

    indexed: dict[str, list[Path]] = {}
    if not source_root.is_dir():
        return indexed
    for metadata_path in source_root.rglob("*.source.json"):
        try:
            document = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
            remote_id = str((document.get("identity") or {}).get("remote_id") or "")
        except (OSError, json.JSONDecodeError, AttributeError):
            continue
        if document.get("schema_version") != "publication-source/v3" or not remote_id:
            continue
        indexed.setdefault(remote_id, []).append(metadata_path)
    return indexed


def _local_item_from_metadata(
    metadata_path: Path,
    collection: dict,
    remote_id: str,
) -> CatalogItem:
    document = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    identity = document.get("identity") or {}
    recorded_collection = document.get("collection") or {}
    if (
        document.get("schema_version") != "publication-source/v3"
        or document.get("state") != "completed"
        or str(identity.get("remote_id") or "") != remote_id
        or recorded_collection.get("id") != collection["id"]
    ):
        raise PublicationTransactionError("metadado local não pertence à entrada do catálogo")
    sources = document.get("sources")
    segments = document.get("segments")
    derivations = document.get("derivations")
    if (
        not isinstance(sources, list)
        or not isinstance(segments, list)
        or not isinstance(derivations, list)
    ):
        raise PublicationTransactionError("metadado local incompleto")
    cover_urls = [
        str(record.get("url") or "")
        for record in sources
        if record.get("format") == "cover" and record.get("url")
    ]
    cover_derivations = [
        record for record in derivations if record.get("format") == "cover"
    ]
    if len(cover_urls) > 1 or bool(cover_urls) != bool(cover_derivations):
        raise PublicationTransactionError("pareamento local de capa ambíguo")
    if any(
        record.get("format") in {"pdf", "epub"} and not record.get("url")
        for record in sources
    ):
        raise PublicationTransactionError("fonte nativa local sem URL")
    assets = tuple(
        CatalogAsset(
            format=str(record["format"]),
            url=str(record["url"]),
            etag=str(record.get("etag") or ""),
            last_modified=str(record.get("last_modified") or ""),
            size=record.get("size") if isinstance(record.get("size"), int) else None,
            remote_hash=str((record.get("hashes") or {}).get("sha256") or ""),
        )
        for record in sources
        if record.get("format") in {"pdf", "epub"} and record.get("url")
    )
    local_segments = tuple(
        CatalogSegment(
            remote_id=str(record.get("remote_id") or ""),
            url=str(record.get("url") or ""),
            order=int(record.get("order") or 0),
            title=str(record.get("title") or ""),
            html="",
        )
        for record in segments
    )
    return CatalogItem(
        remote_id=remote_id,
        collection_id=str(recorded_collection.get("id") or ""),
        collection_name=str(recorded_collection.get("name") or collection.get("name") or ""),
        author_name=str(identity.get("author_original") or ""),
        author_key=str(identity.get("author_key") or ""),
        language_original=str(identity.get("language_original") or ""),
        language=str(identity.get("language") or ""),
        language_path=str(identity.get("language_path") or ""),
        publication_type=str(identity.get("type") or ""),
        title_original=str(identity.get("title_original") or ""),
        title_normalized=str(identity.get("title_normalized") or ""),
        public_url=str(identity.get("public_url") or ""),
        category_name=str(identity.get("category_original") or ""),
        category_path=str(identity.get("category") or ""),
        cover_url=cover_urls[0] if len(cover_urls) == 1 else "",
        edition=str(identity.get("edition") or ""),
        assets=assets,
        segments=local_segments,
        local_complete=True,
    )


def preflight_local_publication(
    remote_id: str,
    collection: dict,
    source_root: Path,
    local_index: dict[str, list[Path]],
    download_config: dict,
    title: str = "",
    public_url: str = "",
    author: str = "",
) -> CatalogItem | None:
    """Comprova unidade v3 ou legado completo antes de liberar rede da obra."""

    valid: list[CatalogItem] = []
    for metadata_path in local_index.get(remote_id, []):
        try:
            item = _local_item_from_metadata(metadata_path, collection, remote_id)
            validate_complete_publication(item, source_root)
            if item.segments and preflight_existing_text(item, source_root, download_config) is None:
                continue
            if not item.assets and not item.segments:
                continue
            valid.append(item)
        except (OSError, ValueError, ContractError, PublicationTransactionError):
            continue
    if len(valid) == 1:
        return valid[0]
    if valid or not title or not public_url or not author:
        return None
    return _preflight_legacy_native_publication(
        remote_id,
        title,
        public_url,
        author,
        collection,
        source_root,
    )


def _preflight_legacy_native_publication(
    remote_id: str,
    title: str,
    public_url: str,
    author: str,
    collection: dict,
    source_root: Path,
) -> CatalogItem | None:
    """Pareia catálogo e metadado legado com PDF+EPUB íntegros, sem rede."""

    if _book_id_from_url(public_url) != remote_id:
        return None
    try:
        language, language_path = canonical_language(str(collection["language"]))
        category_name = str(collection["category_name"]).strip()
        category_path = str(collection["category"]).strip()
        publication_type = canonical_publication_type(
            str(collection["type"]), str(collection["language"])
        )
        if (
            not category_name
            or not category_path
            or uri_slug(category_path) != category_path
        ):
            return None
        item = CatalogItem(
            remote_id=remote_id,
            collection_id=str(collection["id"]),
            collection_name=str(collection["name"]),
            author_name=author,
            author_key=str(
                collection.get("default_author_key") or canonical_author_key(author)
            ),
            language_original=str(collection["language"]),
            language=language,
            language_path=language_path,
            publication_type=publication_type,
            title_original=title,
            title_normalized=title,
            public_url=public_url,
            category_name=category_name,
            category_path=category_path,
        )
    except (KeyError, ContractError):
        return None
    identity = item.publication_identity()
    matches: list[CatalogItem] = []
    for directory in _identity_directories(source_root, identity):
        metadata_path = directory / identity.metadata_name()
        if not metadata_path.is_file():
            continue
        try:
            records = read_source_records(metadata_path)
        except ContractError:
            continue
        native = [
            record for record in records if record.get("format") in {"pdf", "epub"}
        ]
        if len(native) != 2 or {record.get("format") for record in native} != {
            "pdf",
            "epub",
        }:
            continue
        assets: list[CatalogAsset] = []
        paths: list[Path] = []
        for record in native:
            url = str(record.get("url") or "")
            existing = preflight_existing_asset(url, identity, source_root)
            if existing is None or existing[0].parent.resolve() != directory.resolve():
                break
            normalized = existing[1]
            paths.append(existing[0].resolve())
            assets.append(
                CatalogAsset(
                    format=str(normalized["format"]),
                    url=str(normalized["url"]),
                    etag=str(normalized.get("etag") or ""),
                    last_modified=str(normalized.get("last_modified") or ""),
                    size=int(normalized["size"]),
                    remote_hash=str(normalized["hashes"]["sha256"]),
                )
            )
        if len(assets) != 2 or len({path.parent for path in paths}) != 1:
            continue
        matches.append(
            replace(
                item,
                assets=tuple(
                    sorted(
                        assets,
                        key=lambda asset: (asset.format != "epub", asset.url),
                    )
                ),
                local_complete=True,
            )
        )
    return matches[0] if len(matches) == 1 else None


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
        if item.local_complete and not revalidate:
            ledger.transition(
                key,
                "skipped",
                reason="complete-publication-validated-before-detail",
            )
            return {
                "state": "skipped",
                "downloaded": 0,
                "skipped": 1,
                "extracted": 0,
                "converted": 0,
            }
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
            existing_text = preflight_existing_text(item, source_root, download_config)
            if existing_text is not None and not revalidate:
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
            cover_path: Path | None = None
            cover_source: dict | None = None
            cover_derivation: dict | None = None
            if item.cover_url:
                if no_network:
                    ledger.transition(key, "pending", reason="cover-network-disabled")
                    return {
                        "state": "pending",
                        "downloaded": 0,
                        "skipped": 0,
                        "extracted": 0,
                        "converted": 0,
                    }
                cover_path, cover_source, cover_derivation = download_cover(
                    session,
                    item,
                    source_root,
                    download_config,
                )
                installed_assets.append(cover_path)
                downloaded += 1
            markdown_paths, segment_evidence = write_markdown_publication(
                directory,
                item,
            )
            extracted = len(segment_evidence)
            accessed_at = datetime.now(timezone.utc).isoformat()
            epub_path = generate_epub(
                directory / identity.asset_name("epub", "derived"),
                item,
                markdown_paths,
                cover_path=cover_path,
                accessed_at=accessed_at,
            )
            installed_assets.append(epub_path)
            expected_markdown = {path.name: path.read_bytes() for path in markdown_paths}
            temporary_root = Path(download_config.get("_download_tmp_dir", directory))
            temporary_root.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(
                prefix="markdown-roundtrip-",
                dir=temporary_root,
            ) as restoration_directory:
                restored = restore_markdown_from_epub(epub_path, Path(restoration_directory))
                restored_markdown = {path.name: path.read_bytes() for path in restored}
                if restored_markdown != expected_markdown:
                    raise ContractError("round trip Markdown EPUB divergente")
            epub_hashes = hash_file(epub_path)
            converted = 1
            segment_sources = [
                {
                    "format": "text",
                    "url": evidence["url"],
                    "method": "text-extraction",
                    "accessed_at": accessed_at,
                    "size": len(
                        (directory / evidence["path"]).read_bytes()
                    ),
                    "hashes": {"sha256": evidence["sha256"]},
                }
                for evidence in segment_evidence
            ]
            if cover_source is not None:
                segment_sources.append(cover_source)
            derivations = [
                {
                    "format": "epub",
                    "method": "local-conversion",
                    "path": epub_path.relative_to(directory).as_posix(),
                    "generator": "egwSearch/FT-012",
                    "source": "text/0000-metadata.json",
                    "accessed_at": accessed_at,
                    "hashes": epub_hashes.as_dict(),
                    "size": epub_hashes.size,
                }
            ]
            if cover_derivation is not None:
                derivations.append(cover_derivation)
            for evidence, markdown_path in zip(segment_evidence, markdown_paths, strict=True):
                evidence["path"] = (
                    f"{epub_path.name}!/META-INF/egwsearch-source/{markdown_path.name}"
                )
            text_metadata_path = directory / "text" / "0000-metadata.json"
            original_text_metadata = json.loads(text_metadata_path.read_text(encoding="utf-8"))
            reversible_text_metadata = {
                **original_text_metadata,
                "segments": segment_evidence,
                "reversible_epub": epub_path.name,
            }
            try:
                write_json_atomic(text_metadata_path, reversible_text_metadata)
                for markdown_path in markdown_paths:
                    markdown_path.unlink()
                _write_v3_metadata(
                    source_root,
                    item,
                    "completed",
                    segment_sources,
                    segments=segment_evidence,
                    derivations=derivations,
                )
            except Exception:
                restore_markdown_from_epub(epub_path, directory / "text")
                write_json_atomic(text_metadata_path, original_text_metadata)
                raise
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
    browser_manager: BrowserSessionManager | None = None,
    publisher: GitPublicationPublisher | None = None,
    publication_query: str | None = None,
    local_index: dict[str, list[Path]] | None = None,
    restart: bool = False,
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
    checkpoint_path = _collection_checkpoint_path(
        state_root,
        collection,
        limit,
        publication_query,
    )
    if restart:
        checkpoint_path.unlink(missing_ok=True)
        print(
            f"COLLECTION_RESTART collection={collection['id']} "
            f"checkpoint={checkpoint_path.name}"
        )
    checkpoint = _load_collection_checkpoint(
        checkpoint_path,
        collection,
        limit,
        publication_query,
    )
    session = runtime["requests"].Session() if runtime else None
    if session is not None:
        session.headers["User-Agent"] = download_config["user_agent"]
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
        "resumed": 0,
    }
    try:
        if checkpoint is not None and checkpoint.get("discovery_complete"):
            items = list(checkpoint["_items"])
            print(
                f"COLLECTION_RESUME collection={collection['id']} "
                f"confirmed={len(checkpoint['confirmed_remote_ids'])} "
                f"publications={len(items)}"
            )
        elif fixture_payload is not None:
            items = parse_catalog_payload(fixture_payload, collection)
            if publication_query:
                query = publication_query.casefold().strip()
                items = [
                    item
                    for item in items
                    if query in item.title_original.casefold()
                    or query in item.public_url.casefold()
                    or query == item.remote_id.casefold()
                ]
                if not items:
                    raise ContractError(
                        f"publicação não encontrada na coleção: {publication_query}"
                    )
            if limit is not None:
                items = items[:limit]
            checkpoint = checkpoint or _new_collection_checkpoint(
                collection, limit, publication_query
            )
            checkpoint["catalog_entries"] = [
                {
                    "title": item.title_original,
                    "url": item.public_url,
                    "author": item.author_name,
                }
                for item in items
            ]
            checkpoint["items"] = [_catalog_item_record(item) for item in items]
            checkpoint["_items"] = items
            checkpoint["discovery_complete"] = True
            _save_collection_checkpoint(checkpoint_path, checkpoint)
        else:
            if no_network:
                raise ContractError("fixture obrigatoria com --no-network")
            if browser_manager is None:
                raise ContractError("gerenciador de navegador ausente")
            items = browser_manager.discover_catalog_items(
                collection,
                limiter,
                limit=limit,
                publication_query=publication_query,
                local_preflight=(
                    None
                    if revalidate
                    else lambda remote_id, title, url, author: preflight_local_publication(
                        remote_id,
                        collection,
                        source_root,
                        local_index or {},
                        download_config,
                        title,
                        url,
                        author,
                    )
                ),
                checkpoint_path=checkpoint_path,
                checkpoint=checkpoint,
                restart=restart,
            )
            checkpoint = _load_collection_checkpoint(
                checkpoint_path,
                collection,
                limit,
                publication_query,
            )
            if checkpoint is None:
                raise ContractError("checkpoint de coleção ausente após descoberta")
        if publication_query and fixture_payload is not None:
            query = publication_query.casefold().strip()
            items = [
                item
                for item in items
                if query in item.title_original.casefold()
                or query in item.public_url.casefold()
                or query == item.remote_id.casefold()
            ]
            if not items:
                raise ContractError(
                    f"publicação não encontrada na coleção: {publication_query}"
                )
        if limit is not None:
            items = items[:limit]
        summary["discovered"] = len(items)
        if checkpoint is None:
            checkpoint = _new_collection_checkpoint(collection, limit, publication_query)
            checkpoint["catalog_entries"] = [
                {
                    "title": item.title_original,
                    "url": item.public_url,
                    "author": item.author_name,
                }
                for item in items
            ]
            checkpoint["items"] = [_catalog_item_record(item) for item in items]
            checkpoint["_items"] = items
            checkpoint["discovery_complete"] = True
            _save_collection_checkpoint(checkpoint_path, checkpoint)
        confirmed = set(checkpoint["confirmed_remote_ids"])
        item_remote_ids = [item.remote_id for item in items]
        if len(item_remote_ids) != len(set(item_remote_ids)):
            raise ContractError("catálogo retomável possui identificadores duplicados")
        for position, item in enumerate(items):
            if not item.local_complete or item.remote_id in confirmed:
                continue
            refreshed = None
            if not revalidate:
                refreshed = preflight_local_publication(
                    item.remote_id,
                    collection,
                    source_root,
                    local_index or {},
                    download_config,
                )
            if refreshed is None:
                if browser_manager is None or fixture_payload is not None:
                    raise ContractError(
                        "publicação local mudou durante retomada; rede necessária"
                    )
                entry = checkpoint["catalog_entries"][position]
                refreshed = browser_manager._enrich_book(
                    collection,
                    entry["url"],
                    entry["title"],
                    entry["author"],
                    limiter,
                    restart=restart,
                )
            items[position] = refreshed
            checkpoint["items"] = [_catalog_item_record(value) for value in items]
            checkpoint["_items"] = items
            _save_collection_checkpoint(checkpoint_path, checkpoint)
        for index, item in enumerate(items, 1):
            if item.remote_id in confirmed:
                summary["resumed"] += 1
                print(
                    f"ITEM_RESUMED collection={collection['id']} item={index} "
                    f"remote_id={item.remote_id}"
                )
                continue
            try:
                if publisher is not None:
                    previous = ledger.get(item.stable_key()) or {}
                    publisher.preflight(
                        item,
                        resume=previous.get("git_state") == "commit_pending",
                    )
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
                if publisher is not None and result["state"] in {"completed", "skipped"}:
                    allowlist = validate_complete_publication(item, source_root)
                    commit = publisher.commit(item, allowlist, ledger)
                    if commit:
                        result["commit"] = commit
                        print(
                            f"PUBLICATION_COMMITTED remote_id={item.remote_id} commit={commit}"
                        )
                print(
                    f"ITEM_{result['state'].upper()} collection={collection['id']} "
                    f"item={index} remote_id={item.remote_id} "
                    f"title={json.dumps(item.title_original, ensure_ascii=False)}"
                )
                if result["state"] in {"completed", "skipped", "review_required"}:
                    confirmed.add(item.remote_id)
                    checkpoint["confirmed_remote_ids"] = sorted(confirmed)
                    _save_collection_checkpoint(checkpoint_path, checkpoint)
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
        if (
            not summary["failures"]
            and not summary["blocked"]
            and confirmed == set(item_remote_ids)
        ):
            checkpoint_path.unlink(missing_ok=True)
            print(f"COLLECTION_CHECKPOINT_CLOSED collection={collection['id']}")
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


class _NullProgress:
    def update(self, _size: int) -> None:
        return None

    def close(self) -> None:
        return None


def _selected_collections(config: dict, selected: set[str] | None) -> list[dict]:
    if config["schema_version"] in {2, 3}:
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


def _fixture_source_root(
    canonical_source_root: Path,
    runtime_root: Path,
    output_root: Path | None,
) -> Path:
    """Resolve saída sintética segregada e rejeita sobreposição canônica."""

    candidate = (
        Path(output_root).resolve()
        if output_root is not None
        else (Path(runtime_root) / "tmp" / "fixture-output").resolve()
    )
    canonical = Path(canonical_source_root).resolve()
    if (
        candidate == canonical
        or canonical in candidate.parents
        or candidate in canonical.parents
    ):
        raise ContractError("fixture não pode gravar na raiz canônica de publicações")
    return candidate


def run(
    config_path: Path,
    selected: set[str] | None,
    workers: int | None,
    *,
    limit: int | None = None,
    fixture_path: Path | None = None,
    output_root: Path | None = None,
    no_network: bool = False,
    revalidate: bool = False,
    restart: bool = False,
    commit_per_publication: bool = False,
    publication_query: str | None = None,
) -> int:
    config = load_config(config_path)
    canonical_source_root = resolve_repository_path(config["source_root"], REPOSITORY_ROOT)
    paths = runtime_paths(config, REPOSITORY_ROOT)
    if fixture_path is not None:
        source_root = _fixture_source_root(
            canonical_source_root,
            paths["root"],
            output_root,
        )
    else:
        if output_root is not None:
            raise ContractError("--output-root é exclusivo de --fixture")
        source_root = canonical_source_root
    state_root = paths["acquisition"]
    state_root.mkdir(parents=True, exist_ok=True)
    config["download"]["_download_tmp_dir"] = str(paths["downloads"])
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
    local_index = build_local_publication_index(source_root)
    asset_identity_index = build_asset_identity_index(source_root)
    validate_unique_asset_sha512(asset_identity_index)
    config["download"]["_asset_identity_index"] = asset_identity_index
    shared_limiter = RateLimiter(_rate_policy(config["download"]))
    needs_browser = fixture is None and not no_network
    browser_manager = None
    transaction_enabled = bool(
        commit_per_publication
        or config.get("transaction", {}).get("commit_per_publication", False)
    )
    publisher = None
    if transaction_enabled:
        if worker_count != 1:
            raise ContractError("commit por publicação exige workers=1")
        publisher = GitPublicationPublisher(
            REPOSITORY_ROOT,
            source_root,
            paths["locks"] / "publication-git.lock",
            branch=str(config.get("transaction", {}).get("branch", "dev")),
            index_path=resolve_repository_path(
                str(config["transaction"]["index_path"]),
                REPOSITORY_ROOT,
            ),
        )
    if needs_browser:
        if worker_count != 1:
            raise ContractError(
                "descoberta com navegador persistente exige workers=1"
            )
        browser_manager = BrowserSessionManager(runtime, config["download"], paths)
    try:
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
                        browser_manager=browser_manager,
                        publisher=publisher,
                        publication_query=publication_query,
                        local_index=local_index,
                        restart=restart,
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
                        publisher=publisher,
                        publication_query=publication_query,
                        local_index=local_index,
                        restart=restart,
                    ): collection["id"]
                    for collection in collections
                }
                for future in as_completed(futures):
                    results.append(future.result())
    finally:
        if browser_manager is not None:
            browser_manager.close()
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
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Descarta checkpoints do escopo selecionado e inicia nova execução.",
    )
    parser.add_argument(
        "--publication",
        help="ID remoto, URL ou trecho de título para uma publicação específica.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Raiz segregada para artefatos de fixture; nunca pode ser src/publications.",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Cria um commit isolado por publicação completa; exige branch dev limpa no índice.",
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
            output_root=arguments.output_root.resolve() if arguments.output_root else None,
            no_network=arguments.no_network,
            revalidate=arguments.revalidate,
            restart=arguments.restart,
            commit_per_publication=arguments.commit,
            publication_query=arguments.publication,
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
