import math

from telemetry.packet.session import (
    MarshalZone,
    PacketSessionData,
    WeatherForecastSample,
)


def test_packet_session_data_size():
    assert PacketSessionData.SIZE == 753


def test_marshal_zone_roundtrip():
    zone = MarshalZone(0.25, 3)
    b = zone.to_bytes()
    assert len(b) == MarshalZone.SIZE
    decoded = MarshalZone.from_bytes(b)
    assert math.isclose(decoded.zone_start, zone.zone_start, rel_tol=1e-6, abs_tol=1e-6)
    assert decoded.zone_flag == zone.zone_flag


def test_weather_forecast_sample_roundtrip():
    sample = WeatherForecastSample(
        session_type=2,
        time_offset=15,
        weather=4,
        track_temperature=30,
        track_temperature_change=1,
        air_temperature=22,
        air_temperature_change=2,
        rain_percentage=75,
    )
    b = sample.to_bytes()
    assert len(b) == WeatherForecastSample.SIZE
    decoded = WeatherForecastSample.from_bytes(b)
    assert decoded.session_type == sample.session_type
    assert decoded.time_offset == sample.time_offset
    assert decoded.weather == sample.weather
    assert decoded.track_temperature == sample.track_temperature
    assert decoded.track_temperature_change == sample.track_temperature_change
    assert decoded.air_temperature == sample.air_temperature
    assert decoded.air_temperature_change == sample.air_temperature_change
    assert decoded.rain_percentage == sample.rain_percentage
