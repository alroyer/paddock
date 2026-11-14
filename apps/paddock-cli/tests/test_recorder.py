import socket

import pytest
from paddock_cli.recorder import TelemetryRecorder

DATAGRAM = b"\x01\x02telemetry"


def test_record_one_appends_datagram_and_tracks_stats(tmp_path) -> None:
    recorder = TelemetryRecorder("127.0.0.1", 0, tmp_path)
    try:
        output_path = recorder.start()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            sender.sendto(DATAGRAM, recorder.address)

        assert recorder.record_one() == len(DATAGRAM)
        assert recorder.record_one() is None  # receive timeout

        assert recorder.stats.packets == 1
        assert recorder.stats.bytes == len(DATAGRAM)
        assert output_path.parent == tmp_path
        assert output_path.read_bytes() == DATAGRAM
    finally:
        recorder.close()


def test_start_fails_when_port_is_taken(tmp_path) -> None:
    first = TelemetryRecorder("127.0.0.1", 0, tmp_path / "a")
    first.start()
    try:
        _, port = first.address
        second = TelemetryRecorder("127.0.0.1", port, tmp_path / "b")
        with pytest.raises(OSError):
            second.start()
        assert second.output_path is None
        assert not (tmp_path / "b").exists()
    finally:
        first.close()


def test_recorder_cleans_up_on_close(tmp_path) -> None:
    with TelemetryRecorder("127.0.0.1", 0, tmp_path) as recorder:
        recorder.start()
        recorder.record_one()

    assert recorder._socket is None
    assert recorder._file is None


def test_record_one_before_start_raises(tmp_path) -> None:
    with pytest.raises(RuntimeError, match="not been started"):
        TelemetryRecorder("127.0.0.1", 0, tmp_path).record_one()
