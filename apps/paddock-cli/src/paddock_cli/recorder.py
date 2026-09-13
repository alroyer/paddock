import socket
import threading
from datetime import UTC, datetime
from pathlib import Path


class UDPTelemetryRecorder:
    def __init__(self, host: str, port: int, data_path: Path) -> None:
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
            / f"telemetry_data_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}.bin"
        )
        with open(filepath, "wb") as f:
            while self._running:
                try:
                    data, addr = self._socket.recvfrom(65535)
                    f.write(data)
                    print(f"[recorder] Received {len(data)} bytes from {addr}")
                except TimeoutError:
                    continue
                except OSError:
                    break
                if not self._running:
                    break


def create_data_directory(data_path: Path) -> bool:
    """Create the data directory if it does not exist yet.

    Returns True if it was created, False if it already existed.
    """
    if data_path.exists():
        return False
    data_path.mkdir(parents=True)
    return True
