from helpers import make_header
from telemetry.packet.car_telemetry import CarTelemetryData, PacketCarTelemetryData
from telemetry.packet.header import PacketHeader


def test_packet_car_telemetry_data_size():
    assert PacketCarTelemetryData.SIZE == 1352


def test_car_telemetry_roundtrip():
    ct = CarTelemetryData(
        speed=200,
        throttle=0.85,
        steer=-0.1,
        brake=0.0,
        clutch=0,
        gear=5,
        engine_rpm=12000,
        drs=0,
        rev_lights_percent=75,
        rev_lights_bit_value=0x7FFF,
        brakes_temperature=(250, 260, 270, 280),
        tyres_surface_temperature=(85, 87, 83, 89),
        tyres_inner_temperature=(90, 92, 88, 94),
        engine_temperature=95,
        tyres_pressure=(28.5, 28.3, 27.9, 28.1),
        surface_type=(0, 0, 0, 0),
    )
    b = ct.to_bytes()
    assert len(b) == CarTelemetryData.SIZE
    ct2 = CarTelemetryData.from_bytes(b)
    assert ct2.speed == ct.speed
    assert ct2.gear == ct.gear
    assert ct2.engine_rpm == ct.engine_rpm


def test_packet_car_telemetry_roundtrip():
    header = make_header(6)

    cars = [
        CarTelemetryData(
            speed=200 + i * 5,
            throttle=0.85 - i * 0.01,
            steer=-0.1 + i * 0.01,
            brake=0.0,
            clutch=0,
            gear=5,
            engine_rpm=12000,
            drs=0,
            rev_lights_percent=75,
            rev_lights_bit_value=0x7FFF,
            brakes_temperature=(250, 260, 270, 280),
            tyres_surface_temperature=(85, 87, 83, 89),
            tyres_inner_temperature=(90, 92, 88, 94),
            engine_temperature=95,
            tyres_pressure=(28.5, 28.3, 27.9, 28.1),
            surface_type=(0, 0, 0, 0),
        )
        for i in range(22)
    ]

    pct = PacketCarTelemetryData(
        header=header,
        car_telemetry_data=tuple(cars),
        mfd_panel_index=0,
        mfd_panel_index_secondary_player=255,
        suggested_gear=5,
    )

    b = pct.to_bytes()
    assert len(b) == PacketCarTelemetryData.SIZE

    header, remaining = PacketHeader.parse(b)
    pct2, remaining = PacketCarTelemetryData.parse(header, remaining)
    assert remaining == b""
    assert pct2.header.packet_format == header.packet_format
    assert len(pct2.car_telemetry_data) == 22
    assert pct2.car_telemetry_data[0].speed == cars[0].speed
    assert pct2.mfd_panel_index == 0
    assert pct2.suggested_gear == 5
