from dataclasses import dataclass

import constants


@dataclass
class Header:
    packet_format: int
    game_year: int
    game_major_version: int
    game_minor_version: int
    packet_version: int
    packet_id: int
    session_uid: int
    session_time: float
    frame_identifier: int
    overall_frame_identifier: int
    player_car_index: int
    secondary_player_car_index: int
    secondary_player_car_index: int


@dataclass
class CarMotionData:
    world_position_x: float
    world_position_y: float
    world_position_z: float
    world_velocity_x: float
    world_velocity_y: float
    world_velocity_z: float
    world_forward_dir_x: int
    world_forward_dir_y: int
    world_forward_dir_z: int
    world_right_dir_x: int
    world_right_dir_y: int
    world_right_dir_z: int
    g_force_lateral: float
    g_force_longitudinal: float
    g_force_vertical: float
    yaw: float
    pitch: float
    roll: float


@dataclass
class MarshalZone:
    zone_start: float
    zone_flag: int


if __name__ == '__main__':
    import struct

    with open('./data/telemetry.bin', 'rb') as file:
        data = file.read()
        print(len(data))

        header = Header(*struct.unpack('<HBBBBBQfIIBB', data[:29]))
        print(header)

        event_string_code = ''.join(
            [chr(b) for b in struct.unpack('BBBB', data[29:33])]
        )
        print(event_string_code)

        button_status = struct.unpack('I', data[33:37])[0]
        print(button_status)

        for bit_flag, button in constants.BUTTON_FLAGS.items():
            if bit_flag & button_status:
                print(button)
