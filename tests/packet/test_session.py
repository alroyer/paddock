import struct

import pytest

from src.packet.session import MarshalZone


def test_constructs_marshal_zone(marshal_zone_data):
    marshal_zone = MarshalZone(*struct.unpack(MarshalZone.unpack_format(), marshal_zone_data))

    assert marshal_zone.zone_start == 0
    assert marshal_zone.zone_flag == 0


def test_constructs_weather_forecast_sample():
    assert False


def test_constructs_packet_session_data():
    assert False


@pytest.fixture
def marshal_zone_data():
    data = b''
    return data
