from telemetry.packet.header import PacketHeader
from telemetry.packet.lap_positions import PacketLapPositionsData


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


def test_packet_lap_positions_roundtrip():
    header = _make_header()
    data = PacketLapPositionsData(
        header=header,
        num_laps=3,
        lap_start=0,
        position_for_vehicle_idx=tuple(
            tuple((j + 1) % 256 for j in range(22)) for _ in range(50)
        ),
    )
    b = data.to_bytes()
    assert len(b) == PacketLapPositionsData.SIZE

    decoded = PacketLapPositionsData.from_bytes(b)
    assert decoded.num_laps == 3
    assert decoded.lap_start == 0
    assert decoded.position_for_vehicle_idx[0][0] == 1
    assert decoded.position_for_vehicle_idx[49][21] == 22
