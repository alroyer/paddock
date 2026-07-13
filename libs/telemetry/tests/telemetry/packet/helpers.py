from telemetry.packet.header import PacketHeader


def make_header(packet_id: int) -> PacketHeader:
    return PacketHeader(
        2025,
        25,
        1,
        0,
        1,
        packet_id,
        1234567890123456789,
        12.34,
        100,
        1000,
        0,
        255,
    )
