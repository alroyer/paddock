from telemetry.packet.header import PacketHeader
from telemetry.packet.session_history import (
    LapHistoryData,
    PacketSessionHistoryData,
    TyreStintHistoryData,
)


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


def test_lap_history_roundtrip():
    lh = LapHistoryData(
        lap_time_in_ms=91234,
        sector1_time_ms_part=12345,
        sector1_time_minutes_part=0,
        sector2_time_ms_part=23456,
        sector2_time_minutes_part=0,
        sector3_time_ms_part=34567,
        sector3_time_minutes_part=0,
        lap_valid_bit_flags=0x0F,
    )
    b = lh.to_bytes()
    assert len(b) == LapHistoryData.SIZE
    lh2 = LapHistoryData.from_bytes(b)
    assert lh2.lap_time_in_ms == lh.lap_time_in_ms


def test_tyre_stint_history_roundtrip():
    th = TyreStintHistoryData(
        end_lap=10, tyre_actual_compound=16, tyre_visual_compound=16
    )
    b = th.to_bytes()
    assert len(b) == TyreStintHistoryData.SIZE
    th2 = TyreStintHistoryData.from_bytes(b)
    assert th2.end_lap == 10


def test_packet_session_history_roundtrip():
    hdr = _make_header()
    laps = [LapHistoryData(0, 0, 0, 0, 0, 0, 0, 0)] * 100
    stints = [TyreStintHistoryData(0, 0, 0)] * 8
    pkt = PacketSessionHistoryData(
        header=hdr,
        car_idx=1,
        num_laps=5,
        num_tyre_stints=1,
        best_lap_time_lap_num=3,
        best_sector1_lap_num=2,
        best_sector2_lap_num=2,
        best_sector3_lap_num=3,
        lap_history_data=laps,
        tyre_stints_history_data=stints,
    )
    b = pkt.to_bytes()
    assert len(b) == PacketSessionHistoryData.SIZE
    pkt2 = PacketSessionHistoryData.from_bytes(b)
    assert pkt2.car_idx == 1
    assert len(pkt2.lap_history_data) == 100
