import math

from telemetry.packet.header import PacketHeader
from telemetry.packet.lap import LapData, PacketLapData


def test_lap_data_roundtrip():
    lap = LapData(
        last_lap_time_in_ms=90000,
        current_lap_time_in_ms=45000,
        sector1_time_ms_part=15000,
        sector1_time_minutes_part=0,
        sector2_time_ms_part=15000,
        sector2_time_minutes_part=0,
        delta_to_car_in_front_ms_part=500,
        delta_to_car_in_front_minutes_part=0,
        delta_to_race_leader_ms_part=1000,
        delta_to_race_leader_minutes_part=0,
        lap_distance=1.234,
        total_distance=12.345,
        safety_car_delta=0.0,
        car_position=5,
        current_lap_num=2,
        pit_status=1,
        num_pit_stops=0,
        sector=2,
        current_lap_invalid=0,
        penalties=0,
        total_warnings=0,
        corner_cutting_warnings=0,
        num_unserved_drive_through_pens=0,
        num_unserved_stop_go_pens=0,
        grid_position=5,
        driver_status=3,
        result_status=1,
        pit_lane_timer_active=0,
        pit_lane_time_in_lane_in_ms=0,
        pit_stop_timer_in_ms=0,
        pit_stop_should_serve_pen=0,
        speed_trap_fastest_speed=212.5,
        speed_trap_fastest_lap=3,
    )
    b = lap.to_bytes()
    assert len(b) == LapData.SIZE
    decoded = LapData.from_bytes(b)

    assert decoded.last_lap_time_in_ms == lap.last_lap_time_in_ms
    assert decoded.current_lap_time_in_ms == lap.current_lap_time_in_ms
    assert decoded.sector1_time_ms_part == lap.sector1_time_ms_part
    assert decoded.sector1_time_minutes_part == lap.sector1_time_minutes_part
    assert decoded.sector2_time_ms_part == lap.sector2_time_ms_part
    assert decoded.sector2_time_minutes_part == lap.sector2_time_minutes_part
    assert decoded.delta_to_car_in_front_ms_part == lap.delta_to_car_in_front_ms_part
    assert (
        decoded.delta_to_car_in_front_minutes_part
        == lap.delta_to_car_in_front_minutes_part
    )
    assert decoded.delta_to_race_leader_ms_part == lap.delta_to_race_leader_ms_part
    assert (
        decoded.delta_to_race_leader_minutes_part
        == lap.delta_to_race_leader_minutes_part
    )
    assert math.isclose(
        decoded.lap_distance, lap.lap_distance, rel_tol=1e-6, abs_tol=1e-6
    )
    assert math.isclose(
        decoded.total_distance, lap.total_distance, rel_tol=1e-6, abs_tol=1e-6
    )
    assert math.isclose(
        decoded.safety_car_delta, lap.safety_car_delta, rel_tol=1e-6, abs_tol=1e-6
    )
    assert decoded.car_position == lap.car_position
    assert decoded.current_lap_num == lap.current_lap_num
    assert decoded.pit_status == lap.pit_status
    assert decoded.num_pit_stops == lap.num_pit_stops
    assert decoded.sector == lap.sector
    assert decoded.current_lap_invalid == lap.current_lap_invalid
    assert decoded.penalties == lap.penalties
    assert decoded.total_warnings == lap.total_warnings
    assert decoded.corner_cutting_warnings == lap.corner_cutting_warnings
    assert (
        decoded.num_unserved_drive_through_pens == lap.num_unserved_drive_through_pens
    )
    assert decoded.num_unserved_stop_go_pens == lap.num_unserved_stop_go_pens
    assert decoded.grid_position == lap.grid_position
    assert decoded.driver_status == lap.driver_status
    assert decoded.result_status == lap.result_status
    assert decoded.pit_lane_timer_active == lap.pit_lane_timer_active
    assert decoded.pit_lane_time_in_lane_in_ms == lap.pit_lane_time_in_lane_in_ms
    assert decoded.pit_stop_timer_in_ms == lap.pit_stop_timer_in_ms
    assert decoded.pit_stop_should_serve_pen == lap.pit_stop_should_serve_pen
    assert math.isclose(
        decoded.speed_trap_fastest_speed,
        lap.speed_trap_fastest_speed,
        rel_tol=1e-6,
        abs_tol=1e-6,
    )
    assert decoded.speed_trap_fastest_lap == lap.speed_trap_fastest_lap


def test_packet_lap_data_roundtrip():
    header = PacketHeader(
        2025,
        25,
        1,
        0,
        1,
        2,
        1234567890123456789,
        12.34,
        100,
        1000,
        0,
        255,
    )
    lap = LapData(
        last_lap_time_in_ms=90000,
        current_lap_time_in_ms=45000,
        sector1_time_ms_part=15000,
        sector1_time_minutes_part=0,
        sector2_time_ms_part=15000,
        sector2_time_minutes_part=0,
        delta_to_car_in_front_ms_part=500,
        delta_to_car_in_front_minutes_part=0,
        delta_to_race_leader_ms_part=1000,
        delta_to_race_leader_minutes_part=0,
        lap_distance=1.234,
        total_distance=12.345,
        safety_car_delta=0.0,
        car_position=5,
        current_lap_num=2,
        pit_status=1,
        num_pit_stops=0,
        sector=2,
        current_lap_invalid=0,
        penalties=0,
        total_warnings=0,
        corner_cutting_warnings=0,
        num_unserved_drive_through_pens=0,
        num_unserved_stop_go_pens=0,
        grid_position=5,
        driver_status=3,
        result_status=1,
        pit_lane_timer_active=0,
        pit_lane_time_in_lane_in_ms=0,
        pit_stop_timer_in_ms=0,
        pit_stop_should_serve_pen=0,
        speed_trap_fastest_speed=212.5,
        speed_trap_fastest_lap=3,
    )
    packet = PacketLapData(
        header=header,
        lap_data=[lap] * 22,
        time_trial_pb_car_idx=7,
        time_trial_rival_car_idx=8,
    )

    b = packet.to_bytes()
    assert len(b) == PacketLapData.SIZE
    header, remaining = PacketHeader.parse(b)
    decoded, remaining = PacketLapData.parse(header, remaining)
    assert remaining == b""

    assert math.isclose(
        decoded.header.session_time,
        packet.header.session_time,
        rel_tol=1e-6,
        abs_tol=1e-6,
    )
    assert decoded.header.packet_format == packet.header.packet_format
    assert decoded.header.game_year == packet.header.game_year
    assert decoded.header.game_major_version == packet.header.game_major_version
    assert decoded.header.game_minor_version == packet.header.game_minor_version
    assert decoded.header.packet_version == packet.header.packet_version
    assert decoded.header.packet_id == packet.header.packet_id
    assert decoded.header.session_uid == packet.header.session_uid
    assert decoded.header.frame_identifier == packet.header.frame_identifier
    assert (
        decoded.header.overall_frame_identifier
        == packet.header.overall_frame_identifier
    )
    assert decoded.header.player_car_index == packet.header.player_car_index
    assert (
        decoded.header.secondary_player_car_index
        == packet.header.secondary_player_car_index
    )

    assert len(decoded.lap_data) == 22
    for original, decoded_lap in zip(packet.lap_data, decoded.lap_data):
        assert decoded_lap.car_position == original.car_position
        assert decoded_lap.current_lap_num == original.current_lap_num
        assert decoded_lap.pit_status == original.pit_status
        assert decoded_lap.num_pit_stops == original.num_pit_stops
        assert decoded_lap.sector == original.sector
        assert decoded_lap.current_lap_invalid == original.current_lap_invalid
        assert decoded_lap.penalties == original.penalties
        assert decoded_lap.total_warnings == original.total_warnings
        assert decoded_lap.corner_cutting_warnings == original.corner_cutting_warnings
        assert (
            decoded_lap.num_unserved_drive_through_pens
            == original.num_unserved_drive_through_pens
        )
        assert (
            decoded_lap.num_unserved_stop_go_pens == original.num_unserved_stop_go_pens
        )
        assert decoded_lap.grid_position == original.grid_position
        assert decoded_lap.driver_status == original.driver_status
        assert decoded_lap.result_status == original.result_status
        assert decoded_lap.pit_lane_timer_active == original.pit_lane_timer_active
        assert (
            decoded_lap.pit_lane_time_in_lane_in_ms
            == original.pit_lane_time_in_lane_in_ms
        )
        assert decoded_lap.pit_stop_timer_in_ms == original.pit_stop_timer_in_ms
        assert (
            decoded_lap.pit_stop_should_serve_pen == original.pit_stop_should_serve_pen
        )
        assert math.isclose(
            decoded_lap.lap_distance, original.lap_distance, rel_tol=1e-6, abs_tol=1e-6
        )
        assert math.isclose(
            decoded_lap.total_distance,
            original.total_distance,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            decoded_lap.speed_trap_fastest_speed,
            original.speed_trap_fastest_speed,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert decoded_lap.speed_trap_fastest_lap == original.speed_trap_fastest_lap

    assert decoded.time_trial_pb_car_idx == packet.time_trial_pb_car_idx
    assert decoded.time_trial_rival_car_idx == packet.time_trial_rival_car_idx
