import math

from telemetry.packet.car_status import CarStatusData, PacketCarStatusData
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


def test_car_status_roundtrip():
    cs = CarStatusData(
        traction_control=2,
        anti_lock_brakes=1,
        fuel_mix=3,
        front_brake_bias=54,
        pit_limiter_status=0,
        fuel_in_tank=5.5,
        fuel_capacity=110.0,
        fuel_remaining_laps=12.3,
        max_rpm=15000,
        idle_rpm=8000,
        max_gears=8,
        drs_allowed=1,
        drs_activation_distance=100,
        actual_tyre_compound=16,
        visual_tyre_compound=16,
        tyres_age_laps=2,
        vehicle_fia_flags=0,
        engine_power_ice=250000.0,
        engine_power_mguk=50000.0,
        ers_store_energy=400000.0,
        ers_deploy_mode=2,
        ers_harvested_this_lap_mguk=100.0,
        ers_harvested_this_lap_mguh=50.0,
        ers_deployed_this_lap=75.0,
        network_paused=0,
    )
    b = cs.to_bytes()
    assert len(b) == CarStatusData.SIZE
    cs2 = CarStatusData.from_bytes(b)
    assert cs2.traction_control == cs.traction_control
    assert math.isclose(cs2.fuel_in_tank, cs.fuel_in_tank, rel_tol=1e-6)
    assert cs2.max_rpm == cs.max_rpm


def test_packet_car_status_roundtrip():
    hdr = _make_header()
    one = CarStatusData(
        traction_control=0,
        anti_lock_brakes=1,
        fuel_mix=1,
        front_brake_bias=50,
        pit_limiter_status=1,
        fuel_in_tank=10.0,
        fuel_capacity=110.0,
        fuel_remaining_laps=5.0,
        max_rpm=15000,
        idle_rpm=9000,
        max_gears=7,
        drs_allowed=1,
        drs_activation_distance=0,
        actual_tyre_compound=16,
        visual_tyre_compound=16,
        tyres_age_laps=1,
        vehicle_fia_flags=0,
        engine_power_ice=200000.0,
        engine_power_mguk=45000.0,
        ers_store_energy=300000.0,
        ers_deploy_mode=1,
        ers_harvested_this_lap_mguk=90.0,
        ers_harvested_this_lap_mguh=40.0,
        ers_deployed_this_lap=60.0,
        network_paused=0,
    )
    pkt = PacketCarStatusData(header=hdr, car_status_data=[one] * 22)
    b = pkt.to_bytes()
    assert len(b) == PacketCarStatusData.SIZE
    header, remaining = PacketHeader.parse(b)
    pkt2, remaining = PacketCarStatusData.parse(header, remaining)
    assert remaining == b""
    assert len(pkt2.car_status_data) == 22
    assert pkt2.car_status_data[0].max_gears == one.max_gears
