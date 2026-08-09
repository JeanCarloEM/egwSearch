# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.

"""Modelos universais e validadores de conteúdo editorial estruturado.

O módulo não acessa rede. Ele transforma somente os segmentos HTML já
adquiridos pelo fluxo canônico, falha fechado diante de ambiguidade e grava
JSON determinístico em UTF-8 sem BOM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from typing import Iterable

from acquisition import CatalogItem, CatalogSegment
from publication_contract import ContractError, hash_file, write_json_atomic


SCRIPTURE_SCHEMA = "scripture-corpus/v1"
LEXICAL_SCHEMA = "lexical-corpus/v1"
CONCORDANCE_SCHEMA = "concordance-corpus/v1"
GENERATOR = "egwSearch/structured_content.py"
STRUCTURED_MODELS = frozenset({"scripture", "lexical", "concordance"})
MARK_TAGS = {
    "b": "bold",
    "strong": "bold",
    "i": "italic",
    "em": "italic",
    "sup": "superscript",
    "sub": "subscript",
    "q": "quote",
    "blockquote": "quote",
    "small": "small",
}
BLOCK_TAGS = frozenset({"p", "li", "dt", "dd", "h1", "h2", "h3", "h4", "h5", "h6"})
IGNORED_TAGS = frozenset({"script", "style", "nav", "button", "aside", "footer", "form"})


COMMON_BOOKS = {
    "GEN": ("Genesis", "Gen", "Gn"),
    "EXO": ("Exodus", "Exod", "Ex", "Êxodo", "Exodo"),
    "LEV": ("Leviticus", "Lev", "Lv", "Levítico", "Levitico"),
    "NUM": ("Numbers", "Num", "Nm", "Números", "Numeros"),
    "DEU": ("Deuteronomy", "Deut", "Dt", "Deuteronômio", "Deuteronomio"),
    "JOS": ("Joshua", "Josh", "Js", "Josué", "Josue"),
    "JDG": ("Judges", "Judg", "Jz", "Juízes", "Juizes"),
    "RUT": ("Ruth", "Rt", "Rute"),
    "1SA": ("1 Samuel", "1 Sam", "1Sm"),
    "2SA": ("2 Samuel", "2 Sam", "2Sm"),
    "1KI": ("1 Kings", "1 Kgs", "1Rs", "1 Reis"),
    "2KI": ("2 Kings", "2 Kgs", "2Rs", "2 Reis"),
    "1CH": ("1 Chronicles", "1 Chr", "1Cr", "1 Crônicas", "1 Cronicas"),
    "2CH": ("2 Chronicles", "2 Chr", "2Cr", "2 Crônicas", "2 Cronicas"),
    "EZR": ("Ezra", "Esd", "Esdras"),
    "NEH": ("Nehemiah", "Neh", "Ne", "Neemias"),
    "EST": ("Esther", "Est", "Et", "Ester"),
    "JOB": ("Job", "Jó"),
    "PSA": ("Psalms", "Psalm", "Ps", "Sl", "Salmos", "Salmo"),
    "PRO": ("Proverbs", "Prov", "Pr", "Pv", "Provérbios", "Proverbios"),
    "ECC": ("Ecclesiastes", "Eccl", "Ec", "Eclesiastes"),
    "SNG": ("Song of Solomon", "Song of Songs", "Cant", "Ct", "Cantares"),
    "ISA": ("Isaiah", "Isa", "Is", "Isaías", "Isaias"),
    "JER": ("Jeremiah", "Jer", "Jr", "Jeremias"),
    "LAM": ("Lamentations", "Lam", "Lm", "Lamentações", "Lamentacoes"),
    "EZK": ("Ezekiel", "Ezek", "Ez", "Ezequiel"),
    "DAN": ("Daniel", "Dan", "Dn"),
    "HOS": ("Hosea", "Hos", "Os", "Oseias"),
    "JOL": ("Joel", "Jl"),
    "AMO": ("Amos", "Am"),
    "OBA": ("Obadiah", "Obad", "Ob", "Obadias"),
    "JON": ("Jonah", "Jon", "Jn", "Jonas"),
    "MIC": ("Micah", "Mic", "Mq", "Miqueias"),
    "NAM": ("Nahum", "Nah", "Na", "Naum"),
    "HAB": ("Habakkuk", "Hab", "Hc", "Habacuque"),
    "ZEP": ("Zephaniah", "Zeph", "Sf", "Sofonias"),
    "HAG": ("Haggai", "Hag", "Ag", "Ageu"),
    "ZEC": ("Zechariah", "Zech", "Zc", "Zacarias"),
    "MAL": ("Malachi", "Mal", "Ml", "Malaquias"),
    "MAT": ("Matthew", "Matt", "Mt", "Mateus"),
    "MRK": ("Mark", "Mk", "Mc", "Marcos"),
    "LUK": ("Luke", "Lk", "Lc", "Lucas"),
    "JHN": ("John", "Jn", "Jo", "João", "Joao"),
    "ACT": ("Acts", "At", "Atos"),
    "ROM": ("Romans", "Rom", "Rm", "Romanos"),
    "1CO": ("1 Corinthians", "1 Cor", "1Co", "1 Coríntios", "1 Corintios"),
    "2CO": ("2 Corinthians", "2 Cor", "2Co", "2 Coríntios", "2 Corintios"),
    "GAL": ("Galatians", "Gal", "Gl", "Gálatas", "Galatas"),
    "EPH": ("Ephesians", "Eph", "Ef", "Efésios", "Efesios"),
    "PHP": ("Philippians", "Phil", "Fp", "Filipenses"),
    "COL": ("Colossians", "Col", "Cl", "Colossenses"),
    "1TH": ("1 Thessalonians", "1 Thess", "1Ts", "1 Tessalonicenses"),
    "2TH": ("2 Thessalonians", "2 Thess", "2Ts", "2 Tessalonicenses"),
    "1TI": ("1 Timothy", "1 Tim", "1Tm", "1 Timóteo", "1 Timoteo"),
    "2TI": ("2 Timothy", "2 Tim", "2Tm", "2 Timóteo", "2 Timoteo"),
    "TIT": ("Titus", "Tit", "Tt", "Tito"),
    "PHM": ("Philemon", "Phlm", "Fm", "Filemom"),
    "HEB": ("Hebrews", "Heb", "Hb", "Hebreus"),
    "JAS": ("James", "Jas", "Tg", "Tiago"),
    "1PE": ("1 Peter", "1 Pet", "1Pe", "1 Pedro"),
    "2PE": ("2 Peter", "2 Pet", "2Pe", "2 Pedro"),
    "1JN": ("1 John", "1 Jn", "1Jo", "1 João", "1 Joao"),
    "2JN": ("2 John", "2 Jn", "2Jo", "2 João", "2 Joao"),
    "3JN": ("3 John", "3 Jn", "3Jo", "3 João", "3 Joao"),
    "JUD": ("Jude", "Jud", "Jd", "Judas"),
    "REV": ("Revelation", "Rev", "Ap", "Apocalipse"),
}


class StructuredContentError(ContractError):
    """Sinaliza perda, ambiguidade ou contaminação em conteúdo crítico."""


def _strict_json(raw: str) -> object:
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise StructuredContentError(f"chave JSON duplicada: {key}")
            result[key] = value
        return result

    try:
        return json.loads(
            raw,
            object_pairs_hook=pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                StructuredContentError(f"número JSON não finito: {value}")
            ),
        )
    except json.JSONDecodeError as error:
        raise StructuredContentError("JSON estruturado inválido") from error


@dataclass
class _Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["_Node | str"] = field(default_factory=list)


class _TreeParser(HTMLParser):
    """Constrói árvore HTML mínima preservando ordem e marcas editoriais."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("root")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs) -> None:
        node = _Node(tag.casefold(), {str(k).casefold(): str(v or "") for k, v in attrs})
        self.stack[-1].children.append(node)
        if tag.casefold() not in {"br", "img", "hr", "meta", "link", "input"}:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack[-1].tag == tag.casefold():
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        wanted = tag.casefold()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == wanted:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].children.append(data)


def _nfc_text(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    if "\ufeff" in normalized or any(
        unicodedata.category(character) == "Cc" and character not in "\n\t\r"
        for character in normalized
    ):
        raise StructuredContentError("texto possui BOM ou controle proibido")
    return " ".join(normalized.split())


def _inline_text(value: str) -> str:
    """Normaliza espaços sem apagar fronteiras entre fragmentos marcados."""

    normalized = unicodedata.normalize("NFC", value)
    if "\ufeff" in normalized or any(
        unicodedata.category(character) == "Cc" and character not in "\n\t\r"
        for character in normalized
    ):
        raise StructuredContentError("texto possui BOM ou controle proibido")
    return re.sub(r"\s+", " ", normalized)


def _runs(node: _Node, marks: tuple[str, ...] = ()) -> list[dict]:
    active = marks
    mark = MARK_TAGS.get(node.tag)
    if mark and mark not in active:
        active = (*active, mark)
    style = node.attrs.get("style", "").casefold()
    classes = set(node.attrs.get("class", "").casefold().split())
    inferred_marks = []
    if "font-style:italic" in style.replace(" ", "") or classes & {"italic", "italics", "em"}:
        inferred_marks.append("italic")
    if (
        re.search(r"font-weight\s*:\s*(?:bold|[6-9]00)", style)
        or classes & {"bold", "strong"}
    ):
        inferred_marks.append("bold")
    if "font-variant:small-caps" in style.replace(" ", "") or "small-caps" in classes:
        inferred_marks.append("small-caps")
    for inferred in inferred_marks:
        if inferred not in active:
            active = (*active, inferred)
    alignment = node.attrs.get("align", "").casefold()
    style_alignment = re.search(r"text-align\s*:\s*(left|right|center|justify)", style)
    if not alignment and style_alignment:
        alignment = style_alignment.group(1)
    if alignment in {"left", "right", "center", "justify"}:
        active = (*active, f"align:{alignment}")
    result: list[dict] = []
    for child in node.children:
        if isinstance(child, str):
            text = _inline_text(child)
            if not text.strip():
                continue
            record = {"text": text}
            if active:
                record["marks"] = list(active)
            if result and result[-1].get("marks", []) == record.get("marks", []):
                result[-1]["text"] = f"{result[-1]['text']} {text}".strip()
            else:
                result.append(record)
        elif child.tag == "br":
            result.append({"text": "\n", "marks": [*active, "break"]})
        elif child.tag not in IGNORED_TAGS:
            result.extend(_runs(child, active))
    if result:
        result[0]["text"] = result[0]["text"].lstrip()
        result[-1]["text"] = result[-1]["text"].rstrip()
    return [record for record in result if record["text"]]


def _plain(runs: Iterable[dict]) -> str:
    return "".join(str(run.get("text") or "") for run in runs).strip()


def _slice_runs(runs: list[dict], start: int) -> list[dict]:
    """Remove prefixo por posição preservando as marcas dos fragmentos restantes."""

    result: list[dict] = []
    offset = 0
    for run in runs:
        text = str(run.get("text") or "")
        end = offset + len(text)
        if end <= start:
            offset = end
            continue
        record = dict(run)
        record["text"] = text[max(0, start - offset) :]
        if record["text"]:
            result.append(record)
        offset = end
    if result:
        result[0]["text"] = result[0]["text"].lstrip()
    return [record for record in result if record["text"]]


def _blocks(html: str) -> list[tuple[_Node, list[dict], str]]:
    parser = _TreeParser()
    parser.feed(html)
    parser.close()
    result: list[tuple[_Node, list[dict], str]] = []

    def visit(node: _Node, ignored: bool = False) -> None:
        hidden = ignored or node.tag in IGNORED_TAGS
        if hidden:
            return
        if node.tag in BLOCK_TAGS:
            runs = _runs(node)
            text = _plain(runs)
            if text:
                result.append((node, runs, text))
            return
        for child in node.children:
            if isinstance(child, _Node):
                visit(child, hidden)

    visit(parser.root)
    return result


def _book_registry(options: dict) -> tuple[dict[str, dict], dict[str, str]]:
    configured = options.get("books") if isinstance(options, dict) else None
    books: dict[str, dict] = {}
    if isinstance(configured, dict) and configured:
        for order, (code, raw) in enumerate(configured.items(), 1):
            if not isinstance(raw, dict):
                raise StructuredContentError("metadado de livro inválido")
            name = str(raw.get("name") or "").strip()
            abbreviations = [str(value).strip() for value in raw.get("abbreviations", [])]
            collection = str(raw.get("collection") or options.get("collection") or "BODY")
            if not code or not name or not collection:
                raise StructuredContentError("livro sem código, nome ou coleção")
            books[str(code)] = {
                "name": name,
                "abbreviations": [value for value in abbreviations if value],
                "collection": collection,
                "order": int(raw.get("order") or order),
            }
    else:
        default_collection = str(options.get("collection") or "BODY")
        for order, (code, aliases) in enumerate(COMMON_BOOKS.items(), 1):
            books[code] = {
                "name": aliases[0],
                "abbreviations": list(aliases[1:]),
                "collection": default_collection,
                "order": order,
            }
    aliases: dict[str, str] = {}
    for code, record in books.items():
        for alias in (code, record["name"], *record["abbreviations"]):
            key = unicodedata.normalize("NFKD", alias.casefold())
            key = "".join(c for c in key if not unicodedata.category(c).startswith("M"))
            key = re.sub(r"[^a-z0-9]+", " ", key).strip()
            if key and key not in aliases:
                aliases[key] = code
    return books, aliases


def _fold_reference(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value.casefold())
    folded = "".join(c for c in folded if not unicodedata.category(c).startswith("M"))
    return re.sub(r"[^a-z0-9:]+", " ", folded).strip()


def _reference(value: str, aliases: dict[str, str]) -> tuple[str, str, str, tuple[int, int]] | None:
    candidates = sorted(aliases, key=len, reverse=True)
    if not candidates:
        return None
    normalized = _fold_reference(value)
    match = re.match(
        rf"^({'|'.join(re.escape(alias) for alias in candidates)})\s+(\d+):(\d+[a-z]?)\b",
        normalized,
    )
    if not match:
        return None
    return aliases[match.group(1)], match.group(2), match.group(3), match.span()


def _source_proof(
    item: CatalogItem,
    payload: object,
    counts: dict,
    *,
    accessed_at: str = "",
) -> dict:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "source": {
            "url": item.public_url,
            "collection": item.collection_id,
            "remote_id": item.remote_id,
            "accessed_at": accessed_at,
            "segments": [
                {
                    "remote_id": segment.remote_id,
                    "url": segment.url,
                    "order": segment.order,
                    "sha256": hashlib.sha256(segment.html.encode("utf-8")).hexdigest(),
                }
                for segment in sorted(item.segments, key=lambda value: value.order)
            ],
        },
        "content_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "counts": counts,
        "checks": {"duplicates": 0, "gaps": [], "residual": 0},
        "counterchecks": [],
    }


def scripture_document(item: CatalogItem, *, accessed_at: str = "") -> dict:
    """Materializa um item por versículo e rejeita qualquer ambiguidade."""

    options = dict(item.content_options or {})
    books, aliases = _book_registry(options)
    version = str(options.get("version") or item.publication_identity().acronym.upper())
    collections: dict[str, dict] = {}
    text: dict = {version: {}}
    seen: set[tuple[str, str, str]] = set()
    sequence: dict[tuple[str, str], list[int]] = {}
    verses = 0
    started = False
    for segment in sorted(item.segments, key=lambda value: value.order):
        for node, runs, plain in _blocks(segment.html):
            explicit = {
                "book": node.attrs.get("data-book", ""),
                "chapter": node.attrs.get("data-chapter", ""),
                "verse": node.attrs.get("data-verse", ""),
            }
            if all(explicit.values()):
                code = aliases.get(_fold_reference(explicit["book"]), explicit["book"])
                chapter, verse = explicit["chapter"], explicit["verse"]
                content = runs
            else:
                parsed = _reference(plain, aliases)
                if parsed is None:
                    if started and node.tag in {"p", "li", "dt", "dd"}:
                        raise StructuredContentError(
                            f"texto residual após versículo: {plain[:80]}"
                        )
                    continue
                code, chapter, verse, _span = parsed
                references = re.findall(r"\b\d+:\d+[a-z]?\b", _fold_reference(plain))
                if len(references) != 1:
                    raise StructuredContentError("bloco concatena múltiplos versículos")
                prefix = re.match(r"^.+?\b\d+:\d+[a-z]?\b\s*", plain)
                content = _slice_runs(runs, prefix.end()) if prefix else []
            if not re.fullmatch(r"\d+", chapter) or not re.fullmatch(r"\d+[a-z]?", verse):
                raise StructuredContentError("capítulo ou versículo inválido")
            if not content or not _plain(content):
                raise StructuredContentError("versículo vazio")
            if code not in books:
                books[code] = {
                    "name": explicit.get("book") or code,
                    "abbreviations": [],
                    "collection": str(options.get("collection") or "BODY"),
                    "order": len(books) + 1,
                }
            collection = books[code]["collection"]
            collections.setdefault(
                collection,
                {
                    "name": str((options.get("collections") or {}).get(collection, collection)),
                    "order": len(collections) + 1,
                },
            )
            key = (code, chapter, verse)
            if key in seen:
                raise StructuredContentError(f"versículo duplicado: {code} {chapter}:{verse}")
            seen.add(key)
            started = True
            verses += 1
            bucket = text[version].setdefault(collection, {}).setdefault(code, {}).setdefault(chapter, {})
            bucket[verse] = {"content": content}
            if verse.isdigit():
                sequence.setdefault((code, chapter), []).append(int(verse))
    if not verses:
        raise StructuredContentError("corpus bíblico sem versículos")
    for (code, chapter), values in sequence.items():
        ordered = sorted(values)
        if ordered != list(range(ordered[0], ordered[-1] + 1)):
            raise StructuredContentError(f"lacuna observada em {code} {chapter}")
    used_books = {
        code: record
        for code, record in sorted(books.items(), key=lambda pair: (pair[1]["order"], pair[0]))
        if any(code in collection for collection in text[version].values())
    }
    meta = {
        "versions": {
            version: {
                "name": item.title_original,
                "language": item.language,
                "script": str(options.get("script") or "Latn"),
                "canon": str(options.get("canon") or "source-declared"),
                "versification": str(options.get("versification") or "source-declared"),
            }
        },
        "collections": collections,
        "books": used_books,
    }
    payload = {"meta": meta, "text": text}
    chapter_counts: dict[str, dict] = {}
    ordered_references: list[dict[str, str]] = []
    for collection_code, collection_books in text[version].items():
        collection_counts: dict[str, dict] = {}
        for book_code, chapters in collection_books.items():
            book_counts: dict[str, int] = {}
            for chapter, chapter_verses in chapters.items():
                book_counts[chapter] = len(chapter_verses)
                for verse in chapter_verses:
                    ordered_references.append(
                        {
                            "version": version,
                            "collection": collection_code,
                            "book": book_code,
                            "chapter": chapter,
                            "verse": verse,
                        }
                    )
            collection_counts[book_code] = book_counts
        chapter_counts[collection_code] = collection_counts
    ordered_references.sort(
        key=lambda reference: (
            meta["books"][reference["book"]]["order"],
            int(reference["chapter"]),
            int(re.match(r"\d+", reference["verse"]).group()),
            reference["verse"],
        )
    )
    return {
        "schema": SCRIPTURE_SCHEMA,
        **payload,
        "proof": _source_proof(
            item,
            payload,
            {
                "versions": 1,
                "collections": len(collections),
                "books": len(used_books),
                "verses": verses,
                "by_chapter": {version: chapter_counts},
            },
            accessed_at=accessed_at,
        )
        | {
            "range": {
                "first": ordered_references[0],
                "last": ordered_references[-1],
            }
        },
    }


ENTRY_HEADING_RE = re.compile(r"^\((?P<id>\d+)\)\s*(?P<lemma>[^,]+?)(?:,\s*(?P<romanization>.+))?$")


def _entry_blocks(item: CatalogItem) -> list[tuple[str, str, str, list[str]]]:
    entries: list[tuple[str, str, str, list[str]]] = []
    current: tuple[str, str, str, list[str]] | None = None
    allow_heading = bool((item.content_options or {}).get("heading_entries"))
    for segment in sorted(item.segments, key=lambda value: value.order):
        for block_index, (node, _runs_value, plain) in enumerate(_blocks(segment.html), 1):
            match = ENTRY_HEADING_RE.match(plain) if node.tag.startswith("h") else None
            explicit_id = node.attrs.get("data-lexeme-id") or node.attrs.get("data-entry-id")
            generic_heading = allow_heading and node.tag in {"h4", "h5", "h6"}
            if match or explicit_id or generic_heading:
                if current is not None:
                    entries.append(current)
                identifier = (
                    explicit_id
                    or (match.group("id") if match else "")
                    or node.attrs.get("id")
                    or f"{segment.remote_id}:{block_index}"
                )
                lemma = (
                    node.attrs.get("data-lemma")
                    or (match.group("lemma") if match else plain)
                )
                romanization = node.attrs.get("data-romanization") or (
                    match.group("romanization") if match else ""
                )
                current = (identifier.strip(), _nfc_text(lemma), _nfc_text(romanization or ""), [])
                continue
            if current is not None and node.tag in {"p", "li", "dt", "dd"}:
                current[3].append(plain)
    if current is not None:
        entries.append(current)
    if not entries:
        raise StructuredContentError("conteúdo sem entradas delimitadas")
    identifiers = [entry[0] for entry in entries]
    if len(identifiers) != len(set(identifiers)):
        raise StructuredContentError("entrada lexical/concordância duplicada")
    return entries


def _reference_records(values: Iterable[str], options: dict) -> list[dict]:
    _books, aliases = _book_registry(options)
    candidates = sorted(aliases, key=len, reverse=True)
    pattern = re.compile(
        rf"\b({'|'.join(re.escape(alias) for alias in candidates)})\s+(\d+):(\d+[a-z]?)\b",
        re.IGNORECASE,
    )
    result: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    for value in values:
        folded = _fold_reference(value)
        for match in pattern.finditer(folded):
            key = (aliases[match.group(1)], match.group(2), match.group(3))
            if key in seen:
                continue
            seen.add(key)
            result.append(
                {
                    "version": str(options.get("reference_version") or ""),
                    "book": key[0],
                    "chapter": key[1],
                    "verse": key[2],
                }
            )
    return result


def lexical_document(item: CatalogItem, *, accessed_at: str = "") -> dict:
    """Preserva definição inglesa e mantém tradução em domínio separado."""

    options = dict(item.content_options or {})
    values: dict[str, dict] = {}
    for identifier, lemma, romanization, body in _entry_blocks(item):
        references = _reference_records(body, options)
        definition_parts = [
            part
            for part in body
            if not _reference_records([part], options)
            and not re.fullmatch(r"[A-Za-z]+\s+[A-Z0-9_-]+(?:\.\d+)?", part)
        ]
        if not definition_parts:
            raise StructuredContentError(f"entrada lexical sem definição: {identifier}")
        values[identifier] = {
            "lemma": lemma,
            "language": str(options.get("lemma_language") or ""),
            "script": str(options.get("script") or ""),
            "romanization": romanization,
            "pronunciation": {},
            "ids": {"source": identifier},
            "definitions": {"en": definition_parts},
            "translations": {},
            "references": references,
            "relations": [],
        }
    meta = {
        "title": item.title_original,
        "language": item.language,
        "definition_language": "en",
        "translation_languages": ["pt-BR"],
    }
    payload = {"meta": meta, "entries": dict(sorted(values.items()))}
    return {
        "schema": LEXICAL_SCHEMA,
        **payload,
        "proof": _source_proof(
            item, payload, {"entries": len(values)}, accessed_at=accessed_at
        ),
    }


def concordance_document(item: CatalogItem, *, accessed_at: str = "") -> dict:
    """Representa termos, formas e referências sem inventar definições."""

    options = dict(item.content_options or {})
    values: dict[str, dict] = {}
    for identifier, term, romanization, body in _entry_blocks(item):
        references = _reference_records(body, options)
        if not references:
            raise StructuredContentError(f"entrada de concordância sem referência: {identifier}")
        forms = []
        relations = []
        for part in body:
            prefix = part.split(" ", 1)[0].strip()
            if prefix and any(ord(character) > 127 for character in prefix) and prefix not in forms:
                forms.append(prefix)
            part_references = _reference_records([part], options)
            if prefix and part_references:
                relations.append({"form": prefix, "references": part_references})
        values[identifier] = {
            "term": term,
            "romanization": romanization,
            "forms": forms,
            "references": references,
            "indices": [],
            "relations": relations,
        }
    meta = {"title": item.title_original, "language": item.language}
    payload = {"meta": meta, "entries": dict(sorted(values.items()))}
    return {
        "schema": CONCORDANCE_SCHEMA,
        **payload,
        "proof": _source_proof(
            item, payload, {"entries": len(values)}, accessed_at=accessed_at
        ),
    }


def build_structured_document(item: CatalogItem, *, accessed_at: str = "") -> dict:
    """Despacha somente modelos explícitos e confirma o schema produzido."""

    if item.content_model == "scripture":
        return scripture_document(item, accessed_at=accessed_at)
    if item.content_model == "lexical":
        return lexical_document(item, accessed_at=accessed_at)
    if item.content_model == "concordance":
        return concordance_document(item, accessed_at=accessed_at)
    raise StructuredContentError(f"modelo estruturado inválido: {item.content_model}")


def validate_structured_document(document: object, expected_model: str | None = None) -> str:
    """Valida envelope, domínios mínimos e isolamento das unidades críticas."""

    if not isinstance(document, dict):
        raise StructuredContentError("JSON estruturado deve ser objeto")
    schema = document.get("schema")
    model_by_schema = {
        SCRIPTURE_SCHEMA: "scripture",
        LEXICAL_SCHEMA: "lexical",
        CONCORDANCE_SCHEMA: "concordance",
    }
    model = model_by_schema.get(schema)
    if model is None or (expected_model is not None and model != expected_model):
        raise StructuredContentError("schema estruturado divergente")
    expected_root = {"schema", "meta", "text", "proof"} if model == "scripture" else {
        "schema",
        "meta",
        "entries",
        "proof",
    }
    if set(document) != expected_root or not isinstance(document.get("meta"), dict):
        raise StructuredContentError("raiz estruturada divergente")
    proof = document.get("proof")
    if (
        not isinstance(proof, dict)
        or not isinstance(proof.get("source"), dict)
        or not isinstance(proof.get("counts"), dict)
        or not isinstance(proof.get("checks"), dict)
        or not isinstance(proof.get("counterchecks"), list)
        or not re.fullmatch(r"[0-9a-f]{64}", str(proof.get("content_sha256") or ""))
    ):
        raise StructuredContentError("prova estruturada divergente")
    payload_key = "text" if model == "scripture" else "entries"
    payload = {"meta": document["meta"], payload_key: document[payload_key]}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != proof["content_sha256"]:
        raise StructuredContentError("hash interno do conteúdo divergente")
    if model == "scripture":
        text = document.get("text")
        if not isinstance(text, dict) or not text:
            raise StructuredContentError("texto bíblico vazio")
        seen = 0
        for version in text.values():
            for collection in version.values():
                for book in collection.values():
                    for chapter in book.values():
                        for verse in chapter.values():
                            if set(verse) != {"content"} or not isinstance(verse["content"], list):
                                raise StructuredContentError("item de versículo divergente")
                            if not _plain(verse["content"]):
                                raise StructuredContentError("item de versículo vazio")
                            for run in verse["content"]:
                                if (
                                    not isinstance(run, dict)
                                    or set(run) not in ({"text"}, {"text", "marks"})
                                    or not isinstance(run.get("text"), str)
                                    or not run["text"]
                                    or (
                                        "marks" in run
                                        and (
                                            not isinstance(run["marks"], list)
                                            or not all(isinstance(mark, str) and mark for mark in run["marks"])
                                        )
                                    )
                                ):
                                    raise StructuredContentError("fragmento de versículo divergente")
                            seen += 1
        if not seen:
            raise StructuredContentError("texto bíblico sem itens")
    else:
        entries = document.get("entries")
        if not isinstance(entries, dict) or not entries:
            raise StructuredContentError("corpus sem entradas")
        required_entry = (
            {
                "lemma", "language", "script", "romanization", "pronunciation",
                "ids", "definitions", "translations", "references", "relations",
            }
            if model == "lexical"
            else {"term", "romanization", "forms", "references", "indices", "relations"}
        )
        for identifier, entry in entries.items():
            if not identifier or not isinstance(entry, dict) or set(entry) != required_entry:
                raise StructuredContentError("entrada estruturada divergente")
            if model == "lexical" and (
                not isinstance(entry["definitions"], dict)
                or not isinstance(entry["definitions"].get("en"), list)
                or not isinstance(entry["translations"], dict)
            ):
                raise StructuredContentError("definição lexical divergente")
            if not isinstance(entry["references"], list):
                raise StructuredContentError("referências estruturadas divergentes")
    return model


def write_structured_artifact(
    directory: Path,
    item: CatalogItem,
    *,
    accessed_at: str = "",
) -> tuple[Path, dict]:
    """Grava, relê e prova o JSON UTF-8 antes de devolvê-lo à transação."""

    document = build_structured_document(item, accessed_at=accessed_at)
    validate_structured_document(document, item.content_model)
    path = directory / f"{item.publication_identity().acronym}.structured.json"
    write_json_atomic(path, document)
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
        raise StructuredContentError("JSON estruturado não está em UTF-8 sem BOM/LF")
    try:
        reloaded = _strict_json(raw.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise StructuredContentError("JSON estruturado ilegível após escrita") from error
    validate_structured_document(reloaded, item.content_model)
    if reloaded != document:
        raise StructuredContentError("round trip JSON estruturado divergente")
    evidence = hash_file(path)
    return path, {
        "format": "json",
        "method": "structured-json",
        "schema": document["schema"],
        "model": item.content_model,
        "path": path.name,
        "generator": GENERATOR,
        "encoding": "utf-8",
        "hashes": evidence.as_dict(),
        "size": evidence.size,
    }


def validate_structured_artifact(path: Path, expected_model: str | None = None) -> dict:
    """Revalida encoding e schema de artefato existente sem confiar no nome."""

    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise StructuredContentError("JSON estruturado contém BOM")
    try:
        document = _strict_json(raw.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise StructuredContentError("JSON estruturado inválido") from error
    validate_structured_document(document, expected_model)
    return document
