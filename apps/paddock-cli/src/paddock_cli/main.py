import queue
import statistics
import struct
import threading
from pathlib import Path

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from telemetry.analyze import TelemetryDataset
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
        "type [cyan]/bye[/], [cyan]/quit[/] or press [cyan]Ctrl+C[/] to stop."
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


def _format_lap_time(milliseconds: int | None) -> str:
    if not milliseconds or milliseconds < 1:
        return "—"
    minutes, remainder = divmod(milliseconds, 60_000)
    seconds, millis = divmod(remainder, 1_000)
    return f"{minutes}:{seconds:02d}.{millis:03d}"


def _format_delta(milliseconds: int | None) -> str:
    if milliseconds is None:
        return "—"
    sign = "+" if milliseconds >= 0 else "-"
    return f"{sign}{abs(milliseconds) / 1_000:.3f}s"


def _format_pace_gap(milliseconds: int | None) -> str:
    if milliseconds is None:
        return "—"
    if milliseconds < 0:
        return f"{abs(milliseconds) / 1_000:.3f}s ahead"
    return f"{milliseconds / 1_000:.3f}s behind"


def _car_reference(value: str | None, player_car_index: int) -> int | str:
    if value is None:
        return player_car_index
    try:
        return int(value)
    except ValueError:
        return value


@app.command(name="analyze")
def analyze_command(
    filepath: Path = Argument(..., help="Path to the telemetry .bin file"),
    car: str | None = Option(
        None,
        "--car",
        help="Car index or driver name (defaults to the player)",
    ),
) -> None:
    """Analyze a driver's session and suggest ways to improve."""
    try:
        dataset = TelemetryDataset.from_file(filepath)
        reference = _car_reference(car, dataset.index.player_car_index)
        driver = dataset.car(reference)
        laps = dataset.laps(reference)
        valid_laps = [
            lap
            for lap in laps
            if lap["lap_time_ms"] and not lap.get("invalidated", False)
        ]
        clean_laps = [lap for lap in valid_laps if lap.get("pit_status", 0) == 0]
        analysis_laps = clean_laps or valid_laps
        board = dataset.board()
        rivals = [
            row
            for row in board
            if row["car_idx"] != driver["car_idx"] and row["best_lap_ms"]
        ]
        best_rival = min(rivals, key=lambda row: row["best_lap_ms"]) if rivals else None
        fuel = dataset.fuel_profile(reference)
        ers = dataset.ers_usage(reference)
        tyre_stints = dataset.tyre_strategy(reference)
        pit_stops = dataset.pit_stops(reference)
    except (OSError, ValueError, KeyError, struct.error) as exc:
        console.print(f"[bold red]✗ Could not analyze {filepath}:[/] {exc}")
        raise Exit(code=1)

    table = Table(box=None, padding=(0, 2))
    table.add_column(style="grey58", justify="right")
    table.add_column()
    table.add_row("Driver", str(driver["name"]))
    table.add_row("Completed laps", str(len(laps)))
    table.add_row("Best lap", _format_lap_time(driver["best_lap_ms"]))
    if best_rival:
        table.add_row("Best rival", str(best_rival["name"]))
        table.add_row(
            "Gap to best rival",
            _format_pace_gap(driver["best_lap_ms"] - best_rival["best_lap_ms"]),
        )

    if analysis_laps:
        lap_times = [lap["lap_time_ms"] for lap in analysis_laps]
        consistency = statistics.pstdev(lap_times) if len(lap_times) > 1 else 0
        table.add_row(
            "Average valid lap",
            _format_lap_time(round(statistics.mean(lap_times))),
        )
        table.add_row("Consistency", f"±{consistency / 1_000:.3f}s")
    else:
        consistency = None

    invalidated = sum(1 for lap in laps if lap.get("invalidated", False))
    table.add_row("Invalidated laps", str(invalidated))
    table.add_row("Pit stops", str(len(pit_stops)))
    table.add_row("Tyre stints", str(len(tyre_stints)))
    if fuel["consumption_kg_per_lap"] is not None:
        table.add_row(
            "Fuel consumption",
            f"{fuel['consumption_kg_per_lap']:.3f} kg/lap",
        )
    if ers["store_energy_kj"] is not None:
        table.add_row("ERS remaining", f"{ers['store_energy_kj']:.2f} kJ")
    console.print(Panel(table, title="[bold cyan]Session analysis[/]", box=box.ROUNDED))

    recommendations: list[str] = []
    if len(analysis_laps) < 2:
        recommendations.append(
            "Complete at least two clean laps to make the consistency and sector advice reliable."
        )
    if valid_laps:
        best_lap = min(valid_laps, key=lambda lap: lap["lap_time_ms"])
        sectors = dataset.sector_breakdown(reference, best_lap["lap"])
        sector_gaps = [
            (index + 1, sector - best)
            for index, (sector, best) in enumerate(
                zip(sectors["sectors_ms"], sectors["best_sector_ms"])
            )
            if sector and best
        ]
        sector_gaps.sort(key=lambda item: item[1], reverse=True)
        sector_table = Table(box=None, padding=(0, 2))
        sector_table.add_column("Sector", style="grey58")
        sector_table.add_column("Best lap")
        sector_table.add_column("Session best")
        sector_table.add_column("Potential")
        for sector, gap in sector_gaps:
            sector_table.add_row(
                str(sector),
                _format_lap_time(sectors["sectors_ms"][sector - 1]),
                _format_lap_time(sectors["best_sector_ms"][sector - 1]),
                f"+{gap / 1_000:.3f}s",
            )
        if sector_gaps:
            console.print(
                Panel(
                    sector_table, title="[bold]Where time is lost[/]", box=box.ROUNDED
                )
            )
            sector, gap = sector_gaps[0]
            if gap >= 500:
                recommendations.append(
                    f"Work on sector {sector}: it is your biggest opportunity, worth about {gap / 1_000:.3f}s per lap."
                )

    if (
        best_rival
        and driver["best_lap_ms"]
        and driver["best_lap_ms"] > best_rival["best_lap_ms"]
    ):
        recommendations.append(
            f"Use {best_rival['name']}'s pace as a target: you are {_format_pace_gap(driver['best_lap_ms'] - best_rival['best_lap_ms'])}."
        )
    for compound, degradation in dataset.tyre_degradation(reference).items():
        if len(degradation) >= 2:
            first = degradation[0]["lap_time_ms"]
            last = degradation[-1]["lap_time_ms"]
            if last - first >= 1_000:
                compound_name = next(
                    (
                        stint["compound_name"]
                        for stint in tyre_stints
                        if stint["compound"] == compound
                    ),
                    f"compound {compound}",
                )
                recommendations.append(
                    f"Manage {compound_name} wear: lap times lose about {(last - first) / 1_000:.3f}s as the tyres age."
                )
                break

    if invalidated:
        recommendations.append(
            f"Stay within track limits: {invalidated} invalidated lap(s) removed usable practice data."
        )
    if consistency is not None and consistency >= 1_000:
        recommendations.append(
            f"Focus on consistency: your valid laps vary by ±{consistency / 1_000:.3f}s."
        )
    if not recommendations:
        recommendations.append(
            "Keep working on consistency and bring each sector closer to its best performance."
        )

    console.print(
        Panel(
            "\n".join(
                f"[cyan]•[/] {recommendation}" for recommendation in recommendations
            ),
            title="[bold green]Improvement priorities[/]",
            box=box.ROUNDED,
        )
    )


if __name__ == "__main__":
    app()
