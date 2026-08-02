# Repository: https://github.com/JeanCarloEM/egwSearch
# License: MPL-2.0 - https://www.mozilla.org/MPL/2.0/

"""Apresentação humana compartilhada da cadeia de publicações.

A camada limita largura, mantém células em uma linha e distingue execução
isolada de composição embutida. O fallback deliberadamente não emite ANSI e
preserva os mesmos indicadores essenciais para logs e CI.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys
from typing import Iterable, TextIO


MIN_WIDTH = 76
DEFAULT_WIDTH = 112
MAX_WIDTH = 136


def terminal_width(stream: TextIO = sys.stdout) -> int:
    """Calcula uma largura estável antes de construir qualquer tabela."""

    detected = shutil.get_terminal_size((DEFAULT_WIDTH, 24)).columns
    return max(MIN_WIDTH, min(MAX_WIDTH, detected))


def compact_path(value: str | Path, width: int) -> str:
    """Trunca pelo meio, preservando raiz curta e basename identificador."""

    text = str(value).replace("\\", "/")
    if len(text) <= width:
        return text
    if width < 12:
        return text[-width:]
    basename = text.rsplit("/", 1)[-1]
    tail_width = min(len(basename) + 1, max(8, width * 2 // 3))
    head_width = width - tail_width - 1
    return f"{text[:head_width]}…{text[-tail_width:]}"


def _percent(ppm: int | None) -> str:
    return "—" if ppm is None else f"{ppm / 10_000:.1f}%"


class PublicationReporter:
    """Renderiza tabelas compactas e pode ser reutilizado por etapas filhas."""

    def __init__(
        self,
        title: str,
        *,
        embedded: bool = False,
        stream: TextIO = sys.stdout,
        force_terminal: bool | None = None,
        compact: bool = False,
    ) -> None:
        self.title = title
        self.embedded = embedded
        self.stream = stream
        self.compact = compact
        self.width = terminal_width(stream)
        self.terminal = False
        self._rich = False
        self._console = None
        try:
            from rich.console import Console

            terminal = (
                bool(force_terminal)
                if force_terminal is not None
                else bool(getattr(stream, "isatty", lambda: False)())
            )
            self.terminal = terminal
            self._console = Console(
                file=stream,
                width=self.width,
                force_terminal=terminal,
                no_color=bool(os.environ.get("NO_COLOR")) or not terminal,
                soft_wrap=False,
                highlight=False,
            )
            self._rich = True
        except ImportError:
            self._console = None

    def child(self, title: str) -> "PublicationReporter":
        """Compartilha destino e largura sem repetir moldura do processo pai."""

        child = PublicationReporter(
            title,
            embedded=True,
            stream=self.stream,
            compact=self.compact,
        )
        child.width = self.width
        child.terminal = self.terminal
        child._console = self._console
        child._rich = self._rich
        return child

    def start(self, detail: str = "") -> None:
        if self.embedded:
            return
        label = f"{self.title}  {compact_path(detail, self.width - len(self.title) - 4)}".rstrip()
        if self._rich:
            from rich.panel import Panel

            self._console.print(Panel(label, style="bold cyan", expand=True))
        else:
            self.stream.write(f"== {label} ==\n")

    def section(self, title: str, detail: str = "") -> None:
        label = compact_path(detail, max(24, self.width - len(title) - 7))
        if self._rich:
            self._console.rule(f"[bold]{title}[/bold]  {label}", style="blue")
        else:
            self.stream.write(f"-- {title}: {label} --\n")

    def experiments(self, asset: str | Path, rows: Iterable[dict]) -> None:
        values = list(rows)
        if self.compact:
            passed = [row for row in values if row.get("status") == "passed"]
            rejected = [row for row in values if row.get("status") == "rejected"]
            inconclusive = [row for row in values if row.get("status") == "inconclusive"]
            best = next(
                (
                    row
                    for row in passed
                    if row.get("method") not in {"fixed-window", "whole-document"}
                ),
                passed[0] if passed else None,
            )
            accuracy = ((best or {}).get("metrics") or {}).get("accuracy_ppm")
            error = ((best or {}).get("metrics") or {}).get("error_ppm")
            label_width = max(24, self.width - 61)
            label = compact_path(str(asset), label_width)
            line = (
                f"{label:<{label_width}}  "
                f"{str((best or {}).get('method') or 'inconclusive')[:22]:<22}  "
                f"ok={len(passed):>2} erro={len(rejected):>2} inc={len(inconclusive):>2}  "
                f"acerto={_percent(accuracy):>6} erro={_percent(error):>6}"
            )
            if self._rich:
                self._console.print(line, style="green" if passed else "yellow", no_wrap=True, overflow="ellipsis")
            else:
                self.stream.write(line + "\n")
            return
        self.section("Análise", str(asset))
        if self._rich:
            from rich import box
            from rich.table import Table

            table = Table(
                box=box.SIMPLE_HEAVY,
                expand=True,
                show_edge=False,
                pad_edge=False,
            )
            columns = (
                ("Método", "left", 22),
                ("Estado", "center", 12),
                ("Chunks", "right", 8),
                ("Tempo", "right", 9),
                ("Eficiência", "right", 11),
                ("Acerto", "right", 9),
                ("Erro", "right", 9),
                ("Diagnóstico", "left", 25),
            )
            for name, justify, maximum in columns:
                table.add_column(name, justify=justify, no_wrap=True, overflow="ellipsis", max_width=maximum)
            styles = {"passed": "green", "rejected": "red", "inconclusive": "yellow"}
            for row in values:
                metrics = row.get("metrics") or {}
                duration = int(row.get("_duration_ms", row.get("duration_ms", 0)) or 0)
                throughput = int(row.get("_throughput_chars_per_second", row.get("throughput_chars_per_second", 0)) or 0)
                compact_efficiency = int((row.get("efficiency") or {}).get("characters_per_chunk") or 0)
                diagnostics = ",".join(row.get("diagnostics") or ()) or "—"
                status = str(row.get("status") or "inconclusive")
                table.add_row(
                    str(row.get("method") or "—"),
                    f"[{styles.get(status, 'white')}]{status}[/{styles.get(status, 'white')}]",
                    str(row.get("chunk_count") or 0),
                    f"{duration} ms",
                    f"{compact_efficiency} car/ch" if compact_efficiency else (f"{throughput / 1000:.1f} kcar/s" if throughput else "—"),
                    _percent(metrics.get("accuracy_ppm")),
                    _percent(metrics.get("error_ppm")),
                    compact_path(diagnostics, 25),
                )
            self._console.print(table)
        else:
            self.stream.write("método | estado | chunks | ms | kcar/s | acerto | erro | diagnóstico\n")
            for row in values:
                metrics = row.get("metrics") or {}
                self.stream.write(
                    " | ".join(
                        (
                            str(row.get("method") or "—"),
                            str(row.get("status") or "inconclusive"),
                            str(row.get("chunk_count") or 0),
                            str(row.get("_duration_ms", row.get("duration_ms", 0)) or 0),
                            str((row.get("efficiency") or {}).get("characters_per_chunk") or 0),
                            _percent(metrics.get("accuracy_ppm")),
                            _percent(metrics.get("error_ppm")),
                            compact_path(",".join(row.get("diagnostics") or ()) or "—", 25),
                        )
                    )
                    + "\n"
                )

    def result(self, stage: str, fields: dict[str, object]) -> None:
        pairs = [(key, compact_path(str(value), 44)) for key, value in fields.items()]
        if self._rich:
            from rich import box
            from rich.table import Table

            table = Table(box=box.MINIMAL, show_header=False, expand=True, pad_edge=False)
            table.add_column("Campo", style="dim", no_wrap=True, width=18)
            table.add_column("Valor", no_wrap=True, overflow="ellipsis")
            for key, value in pairs:
                table.add_row(key, value)
            self._console.print(f"[bold cyan]{stage}[/bold cyan]")
            self._console.print(table)
        else:
            self.stream.write(f"{stage}: " + " ".join(f"{key}={value}" for key, value in pairs) + "\n")

    def publication_gap(self) -> None:
        self.stream.write("\n\n")

    def error(self, stage: str, error: BaseException | str) -> None:
        value = compact_path(str(error), max(24, self.width - len(stage) - 9))
        if self._rich:
            self._console.print(f"[bold red]{stage}[/bold red]  {value}")
        else:
            self.stream.write(f"ERRO {stage}: {value}\n")
