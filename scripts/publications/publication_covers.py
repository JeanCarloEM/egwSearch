# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Materializa capas públicas determinísticas para todo o índice canônico."""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from urllib.parse import unquote
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from acquisition import CatalogItem
from baixar import OfficialCoverMissing, generate_technical_cover, validate_cover_png
from publication_contract import (
    DEFAULT_CONFIG_PATH,
    REPOSITORY_ROOT,
    load_config,
    resolve_repository_path,
)


class CoverError(RuntimeError):
    """Representa capa ausente, insegura ou inválida."""


def _safe_member(base: str, reference: str) -> str:
    candidate = PurePosixPath(base).parent / unquote(reference.split("#", 1)[0])
    parts: list[str] = []
    for part in candidate.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise CoverError("referência EPUB escapa do pacote")
            parts.pop()
            continue
        parts.append(part)
    if not parts:
        raise CoverError("referência EPUB vazia")
    return "/".join(parts)


def _xml_root(payload: bytes, label: str) -> ElementTree.Element:
    if b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
        raise CoverError(f"XML inseguro no EPUB: {label}")
    try:
        return ElementTree.fromstring(payload)
    except ElementTree.ParseError as error:
        raise CoverError(f"XML inválido no EPUB: {label}") from error


def _epub_cover_bytes(path: Path) -> bytes:
    """Extrai somente a imagem declarada como capa pelo Package Document."""

    try:
        with ZipFile(path) as archive:
            names = set(archive.namelist())
            container_name = "META-INF/container.xml"
            if container_name not in names:
                raise CoverError("EPUB sem container.xml")
            container = _xml_root(archive.read(container_name), container_name)
            rootfile = next(
                (
                    str(element.attrib.get("full-path") or "")
                    for element in container.iter()
                    if element.tag.rsplit("}", 1)[-1] == "rootfile"
                    and element.attrib.get("full-path")
                ),
                "",
            )
            if not rootfile or rootfile not in names:
                raise CoverError("EPUB sem Package Document declarado")
            package = _xml_root(archive.read(rootfile), rootfile)
            manifest: dict[str, tuple[str, str, str]] = {}
            for element in package.iter():
                if element.tag.rsplit("}", 1)[-1] != "item":
                    continue
                item_id = str(element.attrib.get("id") or "")
                href = str(element.attrib.get("href") or "")
                if item_id and href:
                    manifest[item_id] = (
                        href,
                        str(element.attrib.get("media-type") or ""),
                        str(element.attrib.get("properties") or ""),
                    )
            candidates: list[tuple[str, str, str]] = [
                value
                for value in manifest.values()
                if "cover-image" in value[2].split()
            ]
            legacy_id = next(
                (
                    str(element.attrib.get("content") or "")
                    for element in package.iter()
                    if element.tag.rsplit("}", 1)[-1] == "meta"
                    and str(element.attrib.get("name") or "").casefold() == "cover"
                ),
                "",
            )
            if legacy_id in manifest:
                candidates.append(manifest[legacy_id])
            candidates.extend(
                value
                for value in manifest.values()
                if value[1].startswith("image/")
                and "cover" in PurePosixPath(value[0]).name.casefold()
            )
            for href, media_type, _properties in candidates:
                member = _safe_member(rootfile, href)
                if member in names and media_type.startswith("image/"):
                    return archive.read(member)
    except (BadZipFile, OSError) as error:
        raise CoverError(f"EPUB ilegível: {path}") from error
    raise CoverError(f"EPUB sem imagem de capa declarada: {path}")


def _normalize_cover(raw: bytes, target: Path, download_config: dict) -> None:
    from PIL import Image, ImageOps

    maximum_pixels = int(download_config.get("cover_max_pixels", 40_000_000))
    maximum_dimension = int(download_config.get("cover_max_dimension", 800))
    try:
        with Image.open(io.BytesIO(raw)) as opened:
            if opened.width * opened.height > maximum_pixels:
                raise CoverError("capa incorporada excede limite de pixels")
            if (
                opened.format == "PNG"
                and opened.mode == "P"
                and not opened.info
                and opened.width <= maximum_dimension
                and opened.height <= maximum_dimension
            ):
                return
            opened.load()
            image = ImageOps.exif_transpose(opened)
            image = image.convert("RGB")
            image.thumbnail(
                (maximum_dimension, maximum_dimension), Image.Resampling.LANCZOS
            )
            normalized = Image.new("RGB", image.size)
            normalized.paste(image)
            normalized = normalized.quantize(
                colors=256,
                method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.NONE,
            )
            output = io.BytesIO()
            normalized.save(output, format="PNG", optimize=True, compress_level=9)
            payload = output.getvalue()
            if target.is_file() and target.read_bytes() == payload:
                return
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=".cover-public-", suffix=".png.partial", dir=target.parent
            )
            os.close(descriptor)
            try:
                temporary = Path(temporary_name)
                temporary.write_bytes(payload)
                validate_cover_png(temporary, download_config)
                temporary.replace(target)
            finally:
                Path(temporary_name).unlink(missing_ok=True)
    except CoverError:
        raise
    except Exception as error:
        raise CoverError("imagem de capa incorporada inválida") from error


def _catalog_item(entry: dict) -> CatalogItem:
    localization = entry["localization"]
    title = entry["title"]
    author = entry["author"]
    remote_id = str(entry.get("remote_id") or entry["id"].rsplit(":", 1)[-1])
    return CatalogItem(
        remote_id=remote_id,
        collection_id="public-archive",
        collection_name="Acervo público",
        author_name=author["name"],
        author_key=author["key"],
        language_original=localization["language"],
        language=localization["language"],
        language_path=localization["language_path"],
        publication_type=localization["type"],
        title_original=title["original"],
        title_normalized=title["normalized"],
        public_url=str(entry.get("public_url") or ""),
        category_name=localization["category"],
        category_path=localization["category"],
    )


def ensure_publication_covers(
    source_root: Path,
    index_path: Path,
    config: dict,
    write: bool,
) -> dict[str, int]:
    """Valida todas as capas e, quando autorizado, materializa as ausentes."""

    document = json.loads(index_path.read_text(encoding="utf-8-sig"))
    publications = document.get("publications")
    if not isinstance(publications, list) or not publications:
        raise CoverError("índice global sem publicações")
    download_config = dict(config.get("download") or {})
    counters = {"valid": 0, "optimized": 0, "embedded": 0, "technical": 0}
    for entry in publications:
        directory = (source_root / entry["path"]).resolve()
        if source_root.resolve() not in directory.parents:
            raise CoverError("path de publicação fora da raiz")
        target = directory / "cover.png"
        if target.is_file():
            validate_cover_png(target, download_config)
            if write:
                previous = target.read_bytes()
                _normalize_cover(previous, target, download_config)
                if target.read_bytes() != previous:
                    counters["optimized"] += 1
            counters["valid"] += 1
            continue
        if not write:
            raise CoverError(f"publicação sem cover.png: {entry['path']}")
        embedded = False
        for asset in entry.get("assets") or []:
            if asset.get("format") != "epub":
                continue
            epub = source_root / asset["path"]
            try:
                _normalize_cover(_epub_cover_bytes(epub), target, download_config)
                counters["embedded"] += 1
                embedded = True
                break
            except CoverError:
                continue
        if embedded:
            continue
        item = _catalog_item(entry)
        with tempfile.TemporaryDirectory(prefix="egwsearch-cover-") as temporary_root:
            generated, _source, _derivation = generate_technical_cover(
                item,
                Path(temporary_root),
                download_config,
                OfficialCoverMissing("", "capa incorporada ausente", ""),
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            generated.replace(target)
            validate_cover_png(target, download_config)
        counters["technical"] += 1
    return counters


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Valida ou materializa cover.png para todo o índice global."
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    args = parser.parse_args(argv)
    config_path = resolve_repository_path(args.config, REPOSITORY_ROOT)
    config = load_config(config_path)
    source_root = resolve_repository_path(config["source_root"], REPOSITORY_ROOT)
    index_path = resolve_repository_path(
        config["intelligence"]["index_path"], REPOSITORY_ROOT
    )
    counters = ensure_publication_covers(source_root, index_path, config, args.write)
    print(
        "PUBLICATION_COVERS_OK "
        f"valid={counters['valid']} optimized={counters['optimized']} "
        f"embedded={counters['embedded']} "
        f"technical={counters['technical']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
