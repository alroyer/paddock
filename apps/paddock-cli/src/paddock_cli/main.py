import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from typer import Exit, Typer

from .recorder import TelemetryRecorder

load_dotenv()

app = Typer()
console = Console()


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@app.command()
def record_data() -> None:
    """Record incoming UDP telemetry packets into a .bin file."""
    host = _env("PADDOCK_CLI_UDP_HOST", "0.0.0.0")
    port = int(_env("PADDOCK_CLI_UDP_PORT", "20777"))
    data_dir = Path(_env("PADDOCK_CLI_DATA_DIR", "data"))

    recorder = TelemetryRecorder(host, port, data_dir)
    try:
        output_path = recorder.start()
    except OSError as exc:
        console.print(f"[bold red]✗[/] Could not bind {host}:{port} — {exc}")
        raise Exit(code=1)

    bound_host, bound_port = recorder.address
    console.print(f"[bold red]●[/] Listening on [cyan]{bound_host}:{bound_port}[/]")
    console.print(f" [grey58]Writing packets to [cyan]{output_path}[/] — press [cyan]Ctrl+C[/] to stop.[/]")

    try:
        recorder.run()
    except KeyboardInterrupt:
        console.print("\n[grey58]Interrupted — stopping.[/]")
    finally:
        recorder.close()

    stats = recorder.stats
    console.print(
        f"[bold green]✔[/] Recorded [cyan]{stats.packets}[/] packet(s), "
        f"[cyan]{stats.bytes}[/] bytes → [cyan]{output_path}[/]"
    )


if __name__ == "__main__":
    app()
