import math

from telemetry.packet.header import PacketHeader
from telemetry.packet.motion import CarMotionData, PacketMotionData


def test_packet_motion_data_size():
    assert PacketMotionData.SIZE == 1349


def test_car_motion_data_roundtrip():
    motion = CarMotionData(
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        1000,
        -1000,
        500,
        200,
        -200,
        0,
        1.23,
        -4.56,
        7.89,
        0.12,
        -0.34,
        0.56,
    )
    b = motion.to_bytes()
    assert len(b) == CarMotionData.SIZE
    motion2 = CarMotionData.from_bytes(b)

    float_fields = [
        "world_position_x",
        "world_position_y",
        "world_position_z",
        "world_velocity_x",
        "world_velocity_y",
        "world_velocity_z",
        "g_force_lateral",
        "g_force_longitudinal",
        "g_force_vertical",
        "yaw",
        "pitch",
        "roll",
    ]
    for field in float_fields:
        assert math.isclose(
            getattr(motion, field), getattr(motion2, field), rel_tol=1e-6, abs_tol=1e-6
        )

    assert (
        motion.world_forward_dir_x,
        motion.world_forward_dir_y,
        motion.world_forward_dir_z,
        motion.world_right_dir_x,
        motion.world_right_dir_y,
        motion.world_right_dir_z,
    ) == (
        motion2.world_forward_dir_x,
        motion2.world_forward_dir_y,
        motion2.world_forward_dir_z,
        motion2.world_right_dir_x,
        motion2.world_right_dir_y,
        motion2.world_right_dir_z,
    )


def test_packet_motion_data_roundtrip():
    header = PacketHeader(
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
    one_car = CarMotionData(
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        1000,
        -1000,
        500,
        200,
        -200,
        0,
        1.23,
        -4.56,
        7.89,
        0.12,
        -0.34,
        0.56,
    )
    packet = PacketMotionData(header=header, car_motion_data=[one_car] * 22)

    b = packet.to_bytes()
    assert len(b) == PacketMotionData.SIZE

    header, remaining = PacketHeader.parse(b)
    packet2, remaining = PacketMotionData.parse(header, remaining)
    assert remaining == b""
    assert math.isclose(
        packet2.header.session_time,
        packet.header.session_time,
        rel_tol=1e-6,
        abs_tol=1e-6,
    )
    assert (
        packet2.header.packet_format,
        packet2.header.game_year,
        packet2.header.game_major_version,
        packet2.header.game_minor_version,
        packet2.header.packet_version,
        packet2.header.packet_id,
        packet2.header.session_uid,
        packet2.header.frame_identifier,
        packet2.header.overall_frame_identifier,
        packet2.header.player_car_index,
        packet2.header.secondary_player_car_index,
    ) == (
        packet.header.packet_format,
        packet.header.game_year,
        packet.header.game_major_version,
        packet.header.game_minor_version,
        packet.header.packet_version,
        packet.header.packet_id,
        packet.header.session_uid,
        packet.header.frame_identifier,
        packet.header.overall_frame_identifier,
        packet.header.player_car_index,
        packet.header.secondary_player_car_index,
    )
    assert len(packet2.car_motion_data) == 22
    for original, decoded in zip(packet.car_motion_data, packet2.car_motion_data):
        assert math.isclose(
            original.world_position_x,
            decoded.world_position_x,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            original.world_position_y,
            decoded.world_position_y,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            original.world_position_z,
            decoded.world_position_z,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            original.world_velocity_x,
            decoded.world_velocity_x,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            original.world_velocity_y,
            decoded.world_velocity_y,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            original.world_velocity_z,
            decoded.world_velocity_z,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert (
            original.world_forward_dir_x,
            original.world_forward_dir_y,
            original.world_forward_dir_z,
            original.world_right_dir_x,
            original.world_right_dir_y,
            original.world_right_dir_z,
        ) == (
            decoded.world_forward_dir_x,
            decoded.world_forward_dir_y,
            decoded.world_forward_dir_z,
            decoded.world_right_dir_x,
            decoded.world_right_dir_y,
            decoded.world_right_dir_z,
        )
        assert math.isclose(
            original.g_force_lateral,
            decoded.g_force_lateral,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            original.g_force_longitudinal,
            decoded.g_force_longitudinal,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(
            original.g_force_vertical,
            decoded.g_force_vertical,
            rel_tol=1e-6,
            abs_tol=1e-6,
        )
        assert math.isclose(original.yaw, decoded.yaw, rel_tol=1e-6, abs_tol=1e-6)
        assert math.isclose(original.pitch, decoded.pitch, rel_tol=1e-6, abs_tol=1e-6)
        assert math.isclose(original.roll, decoded.roll, rel_tol=1e-6, abs_tol=1e-6)
