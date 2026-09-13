import queue
import threading
from pathlib import Path

from telemetry.filters import filter_packets
from telemetry.loader import load_telemetry
from telemetry.packet import PacketId
from typer import Argument, Option, Typer

from .config import DEFAULT_DATA_PATH, DEFAULT_HOST, DEFAULT_PORT
from .events import RecorderEvent, handle_event
from .recorder import UDPTelemetryRecorder, create_data_directory

app = Typer()


@app.command(name="record")
def record_command(
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

    create_data_directory(data_path)

    event_queue: queue.Queue[RecorderEvent] = queue.Queue()
    recorder = UDPTelemetryRecorder(
        host=host,
        port=port,
        data_path=data_path,
        event_queue=event_queue,
    )
    recorder.start()

    consumer_thread = threading.Thread(
        target=_consume_recorder_events,
        args=(event_queue,),
        daemon=True,
    )
    consumer_thread.start()

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

    consumer_thread.join(timeout=1)


def _consume_recorder_events(event_queue: queue.Queue[RecorderEvent]) -> None:
    while True:
        handle_event(event_queue.get())


@app.command(name="view")
def view_command(
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
