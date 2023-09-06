import struct

import pytest

from src.packet.header import PacketHeader


def test_constructs_packet_header(header_data):
    packet_header = PacketHeader(*struct.unpack(PacketHeader.unpack_format(), header_data))

    assert packet_header.frame_identifier == 0
    assert packet_header.game_major_version == 1
    assert packet_header.game_minor_version == 9
    assert packet_header.game_year == 23
    assert packet_header.overall_frame_identifier == 0
    assert packet_header.packet_format == 2023
    assert packet_header.packet_id == 3
    assert packet_header.packet_version == 1
    assert packet_header.player_car_index == 19
    assert packet_header.secondary_player_car_index == 255
    assert packet_header.session_uid == 0


@pytest.fixture
def header_data():
    data = b'\xe7\x07\x17\x01\t\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00#{\xe5C\x00\x00\x00\x00\x00\x00\x00\x00\x13\xff'
    return data
