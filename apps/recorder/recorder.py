import pathlib
import socket
import threading
from datetime import datetime

import typer

DEFAULT_DATA_PATH = pathlib.Path("./data")
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080

app = typer.Typer()


@app.command()
def main(
    host: str = typer.Option(DEFAULT_HOST, help="Host to bind the server to"),
    port: int = typer.Option(DEFAULT_PORT, help="Port to bind the server to"),
    data_path: pathlib.Path = typer.Option(
        DEFAULT_DATA_PATH, help="Path to the data directory"
    ),
) -> None:
    print(f"""
   _______________/___                     |
  |                   |                    | Host: {host}
  |   [REC] ●         |==\\    /|           | Port: {port}
  |                   |   |==| |           |
  |   ____________    |==/    \\|           | Data path: {data_path}
  |  |____________|   |                    |
  |___________________|                    |
         /     \\                           |
        /       \\                          |
       /         \\                         |

""")

    data_directory_created = _create_data_directory(data_path)
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
            line = input(">>> ")
            if line.strip().lower() in ("/quit", "/bye"):
                break
        except KeyboardInterrupt, EOFError:
            break

    recorder.stop()


class UDPTelemetryRecorder:
    def __init__(self, host: str, port: int, data_path: pathlib.Path) -> None:
        self.host = host
        self.port = port
        self.data_path = data_path
        self._running = False
        self._thread: threading.Thread | None = None
        self._socket: socket.socket | None = None

    def start(self) -> None:
        if self._running:
            print("[recorder] Already running.")
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(0.5)
        self._socket.bind((self.host, self.port))

        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._socket:
            self._socket.close()
        if self._thread:
            self._thread.join(timeout=5)
        print("[recorder] Stopped.")

    def _listen_loop(self) -> None:
        if self._socket is None:
            return

        filepath = (
            self.data_path
            / f"telemetry_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.bin"
        )
        with open(filepath, "wb") as f:
            while self._running:
                try:
                    data, addr = self._socket.recvfrom(65535)
                    f.write(data)
                    print(f"[recorder] Received {len(data)} bytes from {addr}")
                except socket.timeout:
                    continue
                except OSError:
                    break
                if not self._running:
                    break


def _create_data_directory(data_path: pathlib.Path) -> bool:
    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)
        return True
    else:
        return False


if __name__ == "__main__":
    app()
