import queue
import struct
import threading
from pathlib import Path

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from telemetry.filters import filter_packets
from telemetry.loader import load_telemetry
from telemetry.packet import PacketId
from typer import Argument, Exit, Option, Typer

from .config import (
    DEFAULT_DATA_PATH,
    DEFAULT_HOST,
    DEFAULT_PORT,
)
from .events import (
    RecorderEvent,
    RecorderStoppedEvent,
    console,
    handle_event,
)
from .recorder import UDPTelemetryRecorder, create_data_directory

app = Typer()

_BODY = "grey52"
_REC = "bold red"
_TRACK = "green"


def _car_text() -> Text:
    """The little F1 car: grey body, red record dot, green track marks."""
    art = Text(no_wrap=True)

    def body(s: str) -> None:
        art.append(s, _BODY)

    def rec(s: str) -> None:
        art.append(s, _REC)

    def track(s: str) -> None:
        art.append(s, _TRACK)

    body("   _______________/___\n")
    body("  |                   |\n")
    body("  |   ")
    rec("[REC] ●")
    body("         |")
    track("==")
    body("\\    /|\n")
    body("  |                   |   |")
    track("==")
    body("| |\n")
    body("  |   ____________    |")
    track("==")
    body("/    \\\n")
    body("  |  |____________|   |\n")
    body("  |___________________|\n")
    body("         /     \\\n")
    body("        /       \\\n")
    body("       /         \\\n")
    return art


def _info_panel(host: str, port: int, data_path: Path) -> Panel:
    table = Table(box=None, padding=(0, 1))
    table.add_column(style="grey58", justify="right")
    table.add_column()
    table.add_row("Host", host)
    table.add_row("Port", str(port))
    table.add_row("Data path", str(data_path.absolute()))
    return Panel(
        table,
        title="[bold]Paddock Recorder[/]",
        box=box.ROUNDED,
        border_style="blue",
    )


@app.command(name="record")
def record_command(
    host: str = Option(DEFAULT_HOST, help="Host to bind the server to"),
    port: int = Option(DEFAULT_PORT, help="Port to bind the server to"),
    data_path: Path = Option(DEFAULT_DATA_PATH, help="Path to the data directory"),
) -> None:
    """Record UDP telemetry packets into a .bin file."""
    grid = Table.grid(padding=(0, 4))
    grid.add_column(vertical="middle")
    grid.add_column(vertical="middle")
    grid.add_row(_car_text(), _info_panel(host, port, data_path))
    console.print(grid)

    if create_data_directory(data_path):
        console.print(
            f" [bold green]✔[/] Created data directory [grey58]{data_path.absolute()}[/]"
        )
    else:
        console.print(
            f" [grey58]Data directory already exists: {data_path.absolute()}[/]"
        )

    event_queue: queue.Queue[RecorderEvent] = queue.Queue()
    recorder = UDPTelemetryRecorder(
        host=host,
        port=port,
        data_path=data_path,
        event_queue=event_queue,
    )

    try:
        if not recorder.start():
            raise Exit(code=1)
    except OSError as exc:
        console.print(f"[bold red]✗ Could not bind {host}:{port}:[/] {exc}")
        raise Exit(code=1)

    console.print(
        "[bold red]●[/] Listening for telemetry data — "
        "type [cyan]/quit[/] or press [cyan]Ctrl+C[/] to stop."
    )

    consumer_thread = threading.Thread(
        target=_consume_recorder_events,
        args=(event_queue,),
        daemon=True,
    )
    consumer_thread.start()

    while True:
        try:
            line = console.input("[bold cyan]>>>[/] ").strip()
        except KeyboardInterrupt, EOFError:
            break
        match line.lower():
            case "/quit" | "/bye" | "quit" | "bye":
                break
            case "/help" | "help" | "?":
                console.print(" [grey58]Commands: /quit · /bye · /help[/]")
            case "":
                continue
            case _:
                console.print(
                    f" [yellow]Unknown command:[/] {line} [grey58](try /help)[/]"
                )

    recorder.stop()
    consumer_thread.join(timeout=2)


def _consume_recorder_events(event_queue: queue.Queue[RecorderEvent]) -> None:
    while True:
        event = event_queue.get()
        handle_event(event)
        if isinstance(event, RecorderStoppedEvent):
            return


@app.command(name="view")
def view_command(
    filepath: Path = Argument(..., help="Path to the telemetry .bin file"),
    packet_id: PacketId | None = Option(None, help="Only keep packets of this type"),
) -> None:
    """Load a telemetry .bin file and inspect its packets."""
    try:
        packets = load_telemetry(filepath)
    except (ValueError, struct.error) as exc:
        console.print(f"[bold red]✗ Could not parse {filepath}:[/] {exc}")
        raise Exit(code=1)
    console.print(f"Loaded [bold]{len(packets):,}[/] packets")

    if packet_id is not None:
        filtered_packets = filter_packets(packets, packet_id=packet_id)
        console.print(
            f"Found [bold]{len(filtered_packets):,}[/] [cyan]{packet_id.name}[/] packets"
        )


if __name__ == "__main__":
    app()
