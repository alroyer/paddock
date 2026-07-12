import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader


@dataclass(frozen=True)
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

    STRUCT_FMT: ClassVar[str] = "<6f6h6f" if BYTES_ORDER == "little" else ">6f6h6f"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "CarMotionData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        (
            world_position_x,
            world_position_y,
            world_position_z,
            world_velocity_x,
            world_velocity_y,
            world_velocity_z,
            world_forward_dir_x,
            world_forward_dir_y,
            world_forward_dir_z,
            world_right_dir_x,
            world_right_dir_y,
            world_right_dir_z,
            g_force_lateral,
            g_force_longitudinal,
            g_force_vertical,
            yaw,
            pitch,
            roll,
        ) = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])

        return cls(
            world_position_x=world_position_x,
            world_position_y=world_position_y,
            world_position_z=world_position_z,
            world_velocity_x=world_velocity_x,
            world_velocity_y=world_velocity_y,
            world_velocity_z=world_velocity_z,
            world_forward_dir_x=world_forward_dir_x,
            world_forward_dir_y=world_forward_dir_y,
            world_forward_dir_z=world_forward_dir_z,
            world_right_dir_x=world_right_dir_x,
            world_right_dir_y=world_right_dir_y,
            world_right_dir_z=world_right_dir_z,
            g_force_lateral=g_force_lateral,
            g_force_longitudinal=g_force_longitudinal,
            g_force_vertical=g_force_vertical,
            yaw=yaw,
            pitch=pitch,
            roll=roll,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.world_position_x,
            self.world_position_y,
            self.world_position_z,
            self.world_velocity_x,
            self.world_velocity_y,
            self.world_velocity_z,
            self.world_forward_dir_x,
            self.world_forward_dir_y,
            self.world_forward_dir_z,
            self.world_right_dir_x,
            self.world_right_dir_y,
            self.world_right_dir_z,
            self.g_force_lateral,
            self.g_force_longitudinal,
            self.g_force_vertical,
            self.yaw,
            self.pitch,
            self.roll,
        )


@dataclass(frozen=True)
class PacketMotionData(BasePacket):
    header: PacketHeader
    car_motion_data: list[CarMotionData]

    SIZE: ClassVar[int] = PacketHeader.SIZE + 22 * CarMotionData.SIZE

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketMotionData", bytes]:
        car_motion_data, remaining = cls._parse_items(
            data, CarMotionData.SIZE, 22, CarMotionData.from_bytes
        )
        return cls(header=header, car_motion_data=car_motion_data), remaining

    def to_bytes(self) -> bytes:
        data = self.header.to_bytes()
        for cmd in self.car_motion_data:
            data += cmd.to_bytes()
        return data
