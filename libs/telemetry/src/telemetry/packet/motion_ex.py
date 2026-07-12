import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class PacketMotionExData(BasePacket):
    header: PacketHeader
    suspension_position: tuple[float, float, float, float]
    suspension_velocity: tuple[float, float, float, float]
    suspension_acceleration: tuple[float, float, float, float]
    wheel_speed: tuple[float, float, float, float]
    wheel_slip_ratio: tuple[float, float, float, float]
    wheel_slip_angle: tuple[float, float, float, float]
    wheel_lat_force: tuple[float, float, float, float]
    wheel_long_force: tuple[float, float, float, float]
    height_of_cog_above_ground: float
    local_velocity_x: float
    local_velocity_y: float
    local_velocity_z: float
    angular_velocity_x: float
    angular_velocity_y: float
    angular_velocity_z: float
    angular_acceleration_x: float
    angular_acceleration_y: float
    angular_acceleration_z: float
    front_wheels_angle: float
    wheel_vert_force: tuple[float, float, float, float]
    front_aero_height: float
    rear_aero_height: float
    front_roll_angle: float
    rear_roll_angle: float
    chassis_yaw: float
    chassis_pitch: float
    wheel_camber: tuple[float, float, float, float]
    wheel_camber_gain: tuple[float, float, float, float]

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "61f"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketMotionExData", bytes]:
        if len(data) < cls.SIZE:
            raise ValueError(
                f"buffer too small: need {cls.SIZE} bytes, got {len(data)}"
            )

        values = struct.unpack_from(cls.STRUCT_FMT, data)

        return cls(
            header=header,
            suspension_position=tuple(values[0:4]),
            suspension_velocity=tuple(values[4:8]),
            suspension_acceleration=tuple(values[8:12]),
            wheel_speed=tuple(values[12:16]),
            wheel_slip_ratio=tuple(values[16:20]),
            wheel_slip_angle=tuple(values[20:24]),
            wheel_lat_force=tuple(values[24:28]),
            wheel_long_force=tuple(values[28:32]),
            height_of_cog_above_ground=values[32],
            local_velocity_x=values[33],
            local_velocity_y=values[34],
            local_velocity_z=values[35],
            angular_velocity_x=values[36],
            angular_velocity_y=values[37],
            angular_velocity_z=values[38],
            angular_acceleration_x=values[39],
            angular_acceleration_y=values[40],
            angular_acceleration_z=values[41],
            front_wheels_angle=values[42],
            wheel_vert_force=tuple(values[43:47]),
            front_aero_height=values[47],
            rear_aero_height=values[48],
            front_roll_angle=values[49],
            rear_roll_angle=values[50],
            chassis_yaw=values[51],
            chassis_pitch=values[52],
            wheel_camber=tuple(values[53:57]),
            wheel_camber_gain=tuple(values[57:61]),
        ), data[cls.SIZE :]

    def to_bytes(self) -> bytes:
        values = [
            *self.suspension_position,
            *self.suspension_velocity,
            *self.suspension_acceleration,
            *self.wheel_speed,
            *self.wheel_slip_ratio,
            *self.wheel_slip_angle,
            *self.wheel_lat_force,
            *self.wheel_long_force,
            self.height_of_cog_above_ground,
            self.local_velocity_x,
            self.local_velocity_y,
            self.local_velocity_z,
            self.angular_velocity_x,
            self.angular_velocity_y,
            self.angular_velocity_z,
            self.angular_acceleration_x,
            self.angular_acceleration_y,
            self.angular_acceleration_z,
            self.front_wheels_angle,
            *self.wheel_vert_force,
            self.front_aero_height,
            self.rear_aero_height,
            self.front_roll_angle,
            self.rear_roll_angle,
            self.chassis_yaw,
            self.chassis_pitch,
            *self.wheel_camber,
            *self.wheel_camber_gain,
        ]
        return self.header.to_bytes() + struct.pack(self.STRUCT_FMT, *values)
