from telemetry.packet.header import PacketHeader
from telemetry.packet.motion_ex import PacketMotionExData


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


def test_packet_motion_ex_roundtrip():
    packet = PacketMotionExData(
        header=_make_header(),
        suspension_position=(1.0, 2.0, 3.0, 4.0),
        suspension_velocity=(5.0, 6.0, 7.0, 8.0),
        suspension_acceleration=(9.0, 10.0, 11.0, 12.0),
        wheel_speed=(13.0, 14.0, 15.0, 16.0),
        wheel_slip_ratio=(17.0, 18.0, 19.0, 20.0),
        wheel_slip_angle=(21.0, 22.0, 23.0, 24.0),
        wheel_lat_force=(25.0, 26.0, 27.0, 28.0),
        wheel_long_force=(29.0, 30.0, 31.0, 32.0),
        height_of_cog_above_ground=33.0,
        local_velocity_x=34.0,
        local_velocity_y=35.0,
        local_velocity_z=36.0,
        angular_velocity_x=37.0,
        angular_velocity_y=38.0,
        angular_velocity_z=39.0,
        angular_acceleration_x=40.0,
        angular_acceleration_y=41.0,
        angular_acceleration_z=42.0,
        front_wheels_angle=43.0,
        wheel_vert_force=(44.0, 45.0, 46.0, 47.0),
        front_aero_height=48.0,
        rear_aero_height=49.0,
        front_roll_angle=50.0,
        rear_roll_angle=51.0,
        chassis_yaw=52.0,
        chassis_pitch=53.0,
        wheel_camber=(54.0, 55.0, 56.0, 57.0),
        wheel_camber_gain=(58.0, 59.0, 60.0, 61.0),
    )

    b = packet.to_bytes()
    assert len(b) == PacketMotionExData.SIZE + PacketHeader.SIZE

    header, remaining = PacketHeader.parse(b)
    packet2, remaining = PacketMotionExData.parse(header, remaining)
    assert remaining == b""
    assert packet2.header.packet_format == packet.header.packet_format
    assert packet2.suspension_position[0] == 1.0
    assert packet2.wheel_camber_gain[3] == 61.0
