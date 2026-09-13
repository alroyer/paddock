from pathlib import Path

from telemetry.filters import filter_packets
from telemetry.loader import load_telemetry
from telemetry.packet import PacketId
from typer import Argument, Option, Typer

from .recorder import UDPTelemetryRecorder, create_data_directory

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080
DEFAULT_DATA_PATH = Path("./data")

app = Typer()


@app.command()
def record(
    host: str = Option(DEFAULT_HOST, help="Host to bind the server to"),
    port: int = Option(DEFAULT_PORT, help="Port to bind the server to"),
    data_path: Path = Option(DEFAULT_DATA_PATH, help="Path to the data directory"),
) -> None:
    """Record UDP telemetry packets into a .bin file."""
    print(f"""
   _______________/___                     |
  |                   |                    | Host: {host}
  |   [REC] ●         |==\\    /|           | Port: {port}
  |                   |   |==| |           |
  |   ____________    |==/    \\|           | Data path: {data_path.absolute()}
  |  |____________|   |                    |
  |___________________|                    |
         /     \\                           |
        /       \\                          |
       /         \\                         |

""")

    data_directory_created = create_data_directory(data_path)
    print(
        "Data directory created.\n"
        if data_directory_created
        else "Data directory already exists.\n"
    )

    recorder = UDPTelemetryRecorder(
        host=host,
        port=port,
        data_path=data_path,
    )
    recorder.start()

    print("Listening for telemetry data. Type /quit or /bye to stop.")
    while True:
        try:
            line = (input(">>> ")).strip()
            match line.lower():
                case "/quit" | "/bye":
                    break
        except KeyboardInterrupt, EOFError:
            break

    recorder.stop()


@app.command()
def view(
    filepath: Path = Argument(..., help="Path to the telemetry .bin file"),
    packet_id: PacketId | None = Option(None, help="Only keep packets of this type"),
) -> None:
    """Load a telemetry .bin file and inspect its packets."""
    packets = load_telemetry(filepath)
    print(f"Loaded {len(packets)} packets")

    if packet_id is not None:
        filtered_packets = filter_packets(packets, packet_id=packet_id)
        print(f"Found {len(filtered_packets)} {packet_id.name} packets")


if __name__ == "__main__":
    app()
