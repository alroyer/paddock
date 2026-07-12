import math

from telemetry.packet.car_damage import CarDamageData, PacketCarDamageData
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


def test_car_damage_roundtrip():
    cd = CarDamageData(
        tyres_wear=[1.0, 2.0, 3.0, 4.0],
        tyres_damage=[10, 20, 30, 40],
        brakes_damage=[0, 1, 2, 3],
        tyre_blisters=[0, 0, 0, 0],
        front_left_wing_damage=1,
        front_right_wing_damage=2,
        rear_wing_damage=3,
        floor_damage=4,
        diffuser_damage=5,
        sidepod_damage=6,
        drs_fault=0,
        ers_fault=0,
        gear_box_damage=0,
        engine_damage=0,
        engine_mguh_wear=0,
        engine_es_wear=0,
        engine_ce_wear=0,
        engine_ice_wear=0,
        engine_mguk_wear=0,
        engine_tc_wear=0,
        engine_blown=0,
        engine_seized=0,
    )
    b = cd.to_bytes()
    assert len(b) == CarDamageData.SIZE
    cd2 = CarDamageData.from_bytes(b)
    assert cd2.tyres_damage[2] == 30
    assert math.isclose(cd2.tyres_wear[1], 2.0, rel_tol=1e-6)


def test_packet_car_damage_roundtrip():
    hdr = _make_header()
    one = CarDamageData(
        tyres_wear=[1.0, 1.1, 1.2, 1.3],
        tyres_damage=[0, 0, 0, 0],
        brakes_damage=[0, 0, 0, 0],
        tyre_blisters=[0, 0, 0, 0],
        front_left_wing_damage=0,
        front_right_wing_damage=0,
        rear_wing_damage=0,
        floor_damage=0,
        diffuser_damage=0,
        sidepod_damage=0,
        drs_fault=0,
        ers_fault=0,
        gear_box_damage=0,
        engine_damage=0,
        engine_mguh_wear=0,
        engine_es_wear=0,
        engine_ce_wear=0,
        engine_ice_wear=0,
        engine_mguk_wear=0,
        engine_tc_wear=0,
        engine_blown=0,
        engine_seized=0,
    )
    pkt = PacketCarDamageData(header=hdr, car_damage_data=[one] * 22)
    b = pkt.to_bytes()
    assert len(b) == PacketCarDamageData.SIZE
    header, remaining = PacketHeader.parse(b)
    pkt2, remaining = PacketCarDamageData.parse(header, remaining)
    assert remaining == b""
    assert len(pkt2.car_damage_data) == 22
    assert math.isclose(pkt2.car_damage_data[0].tyres_wear[3], 1.3, rel_tol=1e-6)
