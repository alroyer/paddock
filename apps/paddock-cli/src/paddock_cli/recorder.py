"""Record UDP telemetry datagrams into a .bin file."""

import socket
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Self

MAX_UDP_PACKET_SIZE = 65535
RECEIVE_TIMEOUT = 0.5


class RecordingStats:
    """Counters for the packets and bytes recorded by a TelemetryRecorder."""

    def __init__(self) -> None:
        self.packets = 0
        self.bytes = 0

    def add(self, size: int) -> None:
        self.packets += 1
        self.bytes += size


class TelemetryRecorder:
    """Bind a UDP socket and append every received datagram to a .bin file."""

    def __init__(self, host: str, port: int, data_dir: Path) -> None:
        self.host = host
        self.port = port
        self.data_dir = data_dir
        self.output_path: Path | None = None
        self.stats = RecordingStats()
        self._socket: socket.socket | None = None
        self._file: IO[bytes] | None = None

    @property
    def address(self) -> tuple[str, int]:
        """The bound (host, port); raises if the recorder has not been started."""
        if self._socket is None:
            raise RuntimeError("The recorder has not been started.")
        host, port = self._socket.getsockname()
        return host, port

    def start(self) -> Path:
        """Bind the socket, create the output file and return its path."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self._socket.settimeout(RECEIVE_TIMEOUT)
            self._socket.bind((self.host, self.port))
        except OSError:
            self._socket.close()
            self._socket = None
            raise

        self.data_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
        self.output_path = self.data_dir / f"telemetry_{timestamp}.bin"
        self._file = self.output_path.open("wb")
        return self.output_path

    def record_one(self) -> int | None:
        """Receive one datagram and append it to the file.

        Returns the number of bytes recorded, or None on a receive timeout.
        """
        if self._socket is None or self._file is None:
            raise RuntimeError("The recorder has not been started.")
        try:
            data, _ = self._socket.recvfrom(MAX_UDP_PACKET_SIZE)
        except TimeoutError:
            return None
        self._file.write(data)
        self._file.flush()
        self.stats.add(len(data))
        return len(data)

    def run(self) -> None:
        """Record datagrams until interrupted or the socket is closed."""
        while self._socket is not None:
            self.record_one()

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        if self._file is not None:
            self._file.close()
            self._file = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
