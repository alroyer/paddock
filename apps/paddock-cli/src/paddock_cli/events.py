import time
from dataclasses import dataclass
from functools import singledispatch

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@dataclass(frozen=True)
class RecorderEvent:
    message: str


@dataclass(frozen=True)
class RecorderStartedEvent(RecorderEvent):
    output_path: str | None = None


@dataclass(frozen=True)
class RecorderStoppedEvent(RecorderEvent):
    output_path: str | None = None


@dataclass(frozen=True)
class PacketReceivedEvent(RecorderEvent):
    size: int = 0
    source: str = ""


@dataclass
class _SessionStats:
    started_at: float | None = None
    packets: int = 0
    total_bytes: int = 0
    last_source: str | None = None


_stats = _SessionStats()
_last_packet_line_at = 0.0


def _format_bytes(num: int) -> str:
    value = float(num)
    for unit in ("B", "kB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            break
        value /= 1024.0
    return f"{int(value)} B" if unit == "B" else f"{value:,.1f} {unit}"


def _format_duration(seconds: float) -> str:
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


@singledispatch
def handle_event(event: RecorderEvent) -> None:
    console.print(f" [grey58]{event.message}[/]", highlight=False)


@handle_event.register
def handle_started(event: RecorderStartedEvent) -> None:
    global _stats, _last_packet_line_at
    _stats = _SessionStats(started_at=time.monotonic())
    _last_packet_line_at = 0.0


@handle_event.register
def handle_packet_received(event: PacketReceivedEvent) -> None:
    global _last_packet_line_at
    _stats.packets += 1
    _stats.total_bytes += event.size
    if event.source:
        _stats.last_source = event.source

    now = time.monotonic()
    if _stats.packets == 1 or now - _last_packet_line_at >= 1.0:
        console.print(
            " [green]▸[/] [grey58]"
            f"{_stats.packets:,} packets · {_format_bytes(_stats.total_bytes)}"
            f" · last from {_stats.last_source or 'unknown'}[/]",
            highlight=False,
        )
        _last_packet_line_at = now


@handle_event.register
def handle_stopped(event: RecorderStoppedEvent) -> None:
    duration = (
        time.monotonic() - _stats.started_at if _stats.started_at else 0.0
    )

    table = Table(box=None, padding=(0, 2))
    table.add_column(style="grey58", justify="right")
    table.add_column()
    table.add_row("Duration", _format_duration(duration))
    table.add_row("Packets", f"{_stats.packets:,}")
    table.add_row("Data", _format_bytes(_stats.total_bytes))
    table.add_row("Source", _stats.last_source or "—")
    if event.output_path:
        table.add_row("File", f"[bold]{event.output_path}[/]")

    console.print(
        Panel(
            table,
            title="[bold green]●  Recording stopped[/]",
            box=box.ROUNDED,
            border_style="green",
        )
    )
