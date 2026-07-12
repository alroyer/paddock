import math

from telemetry.packet.final_classification import (
    FinalClassificationData,
    PacketFinalClassificationData,
)
from telemetry.packet.header import PacketHeader


def _make_header():
    return PacketHeader(
        2025,
        25,
        1,
        0,
        1,
        0,
        1234567890123456789,
        12.34,
        100,
        1000,
        0,
        255,
    )


def test_final_classification_roundtrip():
    fc = FinalClassificationData(
        position=1,
        num_laps=58,
        grid_position=3,
        points=25,
        num_pit_stops=2,
        result_status=3,
        result_reason=2,
        best_lap_time_in_ms=91234,
        total_race_time=3600.123,
        penalties_time=0,
        num_penalties=0,
        num_tyre_stints=2,
        tyre_stints_actual=[16, 17, 0, 0, 0, 0, 0, 0],
        tyre_stints_visual=[16, 17, 0, 0, 0, 0, 0, 0],
        tyre_stints_end_laps=[10, 30, 0, 0, 0, 0, 0, 0],
    )
    b = fc.to_bytes()
    assert len(b) == FinalClassificationData.SIZE
    fc2 = FinalClassificationData.from_bytes(b)
    assert fc2.position == fc.position
    assert fc2.best_lap_time_in_ms == fc.best_lap_time_in_ms
    assert math.isclose(fc2.total_race_time, fc.total_race_time, rel_tol=1e-6)


def test_packet_final_classification_roundtrip():
    hdr = _make_header()
    one = FinalClassificationData(
        position=2,
        num_laps=57,
        grid_position=5,
        points=18,
        num_pit_stops=3,
        result_status=3,
        result_reason=2,
        best_lap_time_in_ms=81234,
        total_race_time=3700.5,
        penalties_time=5,
        num_penalties=1,
        num_tyre_stints=3,
        tyre_stints_actual=[16, 17, 16, 0, 0, 0, 0, 0],
        tyre_stints_visual=[16, 17, 16, 0, 0, 0, 0, 0],
        tyre_stints_end_laps=[12, 28, 50, 0, 0, 0, 0, 0],
    )
    pkt = PacketFinalClassificationData(
        header=hdr, num_cars=22, classification_data=[one] * 22
    )
    b = pkt.to_bytes()
    assert len(b) == PacketFinalClassificationData.SIZE
    header, remaining = PacketHeader.parse(b)
    pkt2, remaining = PacketFinalClassificationData.parse(header, remaining)
    assert remaining == b""
    assert pkt2.num_cars == 22
    assert len(pkt2.classification_data) == 22
    assert pkt2.classification_data[0].points == one.points
