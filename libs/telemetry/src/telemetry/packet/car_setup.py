import struct
from dataclasses import dataclass
from typing import ClassVar

from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class CarSetupData:
    front_wing: int
    rear_wing: int
    on_throttle: int
    off_throttle: int
    front_camber: float
    rear_camber: float
    front_toe: float
    rear_toe: float
    front_suspension: int
    rear_suspension: int
    front_anti_roll_bar: int
    rear_anti_roll_bar: int
    front_suspension_height: int
    rear_suspension_height: int
    brake_pressure: int
    brake_bias: int
    engine_braking: int
    rear_left_tyre_pressure: float
    rear_right_tyre_pressure: float
    front_left_tyre_pressure: float
    front_right_tyre_pressure: float
    ballast: int
    fuel_load: float

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "4B4f9B4fBf"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "CarSetupData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        unpacked = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])
        (
            front_wing,
            rear_wing,
            on_throttle,
            off_throttle,
            front_camber,
            rear_camber,
            front_toe,
            rear_toe,
            front_suspension,
            rear_suspension,
            front_anti_roll_bar,
            rear_anti_roll_bar,
            front_suspension_height,
            rear_suspension_height,
            brake_pressure,
            brake_bias,
            engine_braking,
            rear_left_tyre_pressure,
            rear_right_tyre_pressure,
            front_left_tyre_pressure,
            front_right_tyre_pressure,
            ballast,
            fuel_load,
        ) = unpacked

        return cls(
            front_wing=front_wing,
            rear_wing=rear_wing,
            on_throttle=on_throttle,
            off_throttle=off_throttle,
            front_camber=front_camber,
            rear_camber=rear_camber,
            front_toe=front_toe,
            rear_toe=rear_toe,
            front_suspension=front_suspension,
            rear_suspension=rear_suspension,
            front_anti_roll_bar=front_anti_roll_bar,
            rear_anti_roll_bar=rear_anti_roll_bar,
            front_suspension_height=front_suspension_height,
            rear_suspension_height=rear_suspension_height,
            brake_pressure=brake_pressure,
            brake_bias=brake_bias,
            engine_braking=engine_braking,
            rear_left_tyre_pressure=rear_left_tyre_pressure,
            rear_right_tyre_pressure=rear_right_tyre_pressure,
            front_left_tyre_pressure=front_left_tyre_pressure,
            front_right_tyre_pressure=front_right_tyre_pressure,
            ballast=ballast,
            fuel_load=fuel_load,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.front_wing,
            self.rear_wing,
            self.on_throttle,
            self.off_throttle,
            self.front_camber,
            self.rear_camber,
            self.front_toe,
            self.rear_toe,
            self.front_suspension,
            self.rear_suspension,
            self.front_anti_roll_bar,
            self.rear_anti_roll_bar,
            self.front_suspension_height,
            self.rear_suspension_height,
            self.brake_pressure,
            self.brake_bias,
            self.engine_braking,
            self.rear_left_tyre_pressure,
            self.rear_right_tyre_pressure,
            self.front_left_tyre_pressure,
            self.front_right_tyre_pressure,
            self.ballast,
            self.fuel_load,
        )


@dataclass(frozen=True)
class PacketCarSetupData:
    header: PacketHeader
    car_setups: list[CarSetupData]
    next_front_wing_value: float

    SIZE: ClassVar[int] = PacketHeader.SIZE + 22 * CarSetupData.SIZE + 4

    @classmethod
    def from_bytes(cls, b: bytes) -> "PacketCarSetupData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        header = PacketHeader.from_bytes(b)
        offset = PacketHeader.SIZE
        car_setups = []
        for _ in range(22):
            cs = CarSetupData.from_bytes(b[offset : offset + CarSetupData.SIZE])
            car_setups.append(cs)
            offset += CarSetupData.SIZE

        next_front_wing_value = struct.unpack(_ENDIAN + "f", b[offset : offset + 4])[0]
        return cls(
            header=header,
            car_setups=car_setups,
            next_front_wing_value=next_front_wing_value,
        )

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        for cs in self.car_setups:
            b += cs.to_bytes()
        b += struct.pack(_ENDIAN + "f", self.next_front_wing_value)
        return b
