import math

from telemetry.packet.car_setup import CarSetupData, PacketCarSetupData
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


def test_car_setup_roundtrip():
    cs = CarSetupData(
        front_wing=1,
        rear_wing=2,
        on_throttle=3,
        off_throttle=4,
        front_camber=0.12,
        rear_camber=0.13,
        front_toe=0.01,
        rear_toe=0.02,
        front_suspension=5,
        rear_suspension=6,
        front_anti_roll_bar=7,
        rear_anti_roll_bar=8,
        front_suspension_height=9,
        rear_suspension_height=10,
        brake_pressure=80,
        brake_bias=55,
        engine_braking=3,
        rear_left_tyre_pressure=20.5,
        rear_right_tyre_pressure=20.6,
        front_left_tyre_pressure=19.5,
        front_right_tyre_pressure=19.6,
        ballast=2,
        fuel_load=34.5,
    )
    b = cs.to_bytes()
    assert len(b) == CarSetupData.SIZE
    cs2 = CarSetupData.from_bytes(b)
    assert cs2.front_wing == cs.front_wing
    assert math.isclose(cs2.front_camber, cs.front_camber, rel_tol=1e-6)
    assert math.isclose(cs2.fuel_load, cs.fuel_load, rel_tol=1e-6)


def test_packet_car_setup_roundtrip():
    hdr = _make_header()
    one = CarSetupData(
        front_wing=1,
        rear_wing=2,
        on_throttle=3,
        off_throttle=4,
        front_camber=0.12,
        rear_camber=0.13,
        front_toe=0.01,
        rear_toe=0.02,
        front_suspension=5,
        rear_suspension=6,
        front_anti_roll_bar=7,
        rear_anti_roll_bar=8,
        front_suspension_height=9,
        rear_suspension_height=10,
        brake_pressure=80,
        brake_bias=55,
        engine_braking=3,
        rear_left_tyre_pressure=20.5,
        rear_right_tyre_pressure=20.6,
        front_left_tyre_pressure=19.5,
        front_right_tyre_pressure=19.6,
        ballast=2,
        fuel_load=34.5,
    )
    pkt = PacketCarSetupData(header=hdr, car_setups=[one] * 22, next_front_wing_value=2.5)
    b = pkt.to_bytes()
    assert len(b) == PacketCarSetupData.SIZE
    pkt2 = PacketCarSetupData.from_bytes(b)
    assert math.isclose(pkt2.next_front_wing_value, 2.5, rel_tol=1e-6)
    assert len(pkt2.car_setups) == 22
    assert pkt2.car_setups[0].rear_wing == 2
