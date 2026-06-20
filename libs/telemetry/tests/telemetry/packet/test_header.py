import math

from telemetry.packet.header import PacketHeader


def test_packet_header_roundtrip():
    hdr = PacketHeader(
        2025,
        25,
        1,
        0,
        1,
        4,
        1234567890123456789,
        12.34,
        100,
        1000,
        0,
        255,
    )
    b = hdr.to_bytes()
    assert len(b) == PacketHeader.SIZE
    hdr2 = PacketHeader.from_bytes(b)
    assert math.isclose(hdr.session_time, hdr2.session_time, rel_tol=1e-6, abs_tol=1e-6)
    assert (
        hdr.packet_format,
        hdr.game_year,
        hdr.game_major_version,
        hdr.game_minor_version,
        hdr.packet_version,
        hdr.packet_id,
        hdr.session_uid,
        hdr.frame_identifier,
        hdr.overall_frame_identifier,
        hdr.player_car_index,
        hdr.secondary_player_car_index,
    ) == (
        hdr2.packet_format,
        hdr2.game_year,
        hdr2.game_major_version,
        hdr2.game_minor_version,
        hdr2.packet_version,
        hdr2.packet_id,
        hdr2.session_uid,
        hdr2.frame_identifier,
        hdr2.overall_frame_identifier,
        hdr2.player_car_index,
        hdr2.secondary_player_car_index,
    )
