from telemetry.packet.header import PacketHeader
from telemetry.packet.tyre_sets import PacketTyreSetsData, TyreSetData


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


def test_tyre_set_roundtrip():
    tyre_set = TyreSetData(
        actual_tyre_compound=3,
        visual_tyre_compound=3,
        wear=45,
        available=1,
        recommended_session=2,
        life_span=5,
        usable_life=10,
        lap_delta_time=-120,
        fitted=1,
    )
    b = tyre_set.to_bytes()
    assert len(b) == TyreSetData.SIZE
    tyre_set2 = TyreSetData.from_bytes(b)
    assert tyre_set2.wear == tyre_set.wear
    assert tyre_set2.lap_delta_time == tyre_set.lap_delta_time


def test_packet_tyre_sets_roundtrip():
    header = _make_header()
    tyre_sets = [
        TyreSetData(
            actual_tyre_compound=i % 10,
            visual_tyre_compound=i % 10,
            wear=i,
            available=1,
            recommended_session=(i % 4),
            life_span=20 - i,
            usable_life=15,
            lap_delta_time=-100 + i,
            fitted=1 if i == 5 else 0,
        )
        for i in range(20)
    ]
    packet = PacketTyreSetsData(
        header=header,
        car_idx=1,
        tyre_set_data=tuple(tyre_sets),
        fitted_idx=5,
    )
    b = packet.to_bytes()
    assert len(b) == PacketTyreSetsData.SIZE
    packet2 = PacketTyreSetsData.from_bytes(b)
    assert packet2.car_idx == packet.car_idx
    assert packet2.fitted_idx == packet.fitted_idx
    assert packet2.tyre_set_data[5].fitted == 1
