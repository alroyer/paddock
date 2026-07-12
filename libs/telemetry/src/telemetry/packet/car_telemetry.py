import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class CarTelemetryData:
    speed: int
    throttle: float
    steer: float
    brake: float
    clutch: int
    gear: int
    engine_rpm: int
    drs: int
    rev_lights_percent: int
    rev_lights_bit_value: int
    brakes_temperature: tuple[int, int, int, int]
    tyres_surface_temperature: tuple[int, int, int, int]
    tyres_inner_temperature: tuple[int, int, int, int]
    engine_temperature: int
    tyres_pressure: tuple[float, float, float, float]
    surface_type: tuple[int, int, int, int]

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "H3fBbH2BH4H4B4BH4f4B"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "CarTelemetryData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        (
            speed,
            throttle,
            steer,
            brake,
            clutch,
            gear,
            engine_rpm,
            drs,
            rev_lights_percent,
            rev_lights_bit_value,
            brakes_temperature0,
            brakes_temperature1,
            brakes_temperature2,
            brakes_temperature3,
            tyres_surface_temperature0,
            tyres_surface_temperature1,
            tyres_surface_temperature2,
            tyres_surface_temperature3,
            tyres_inner_temperature0,
            tyres_inner_temperature1,
            tyres_inner_temperature2,
            tyres_inner_temperature3,
            engine_temperature,
            tyres_pressure0,
            tyres_pressure1,
            tyres_pressure2,
            tyres_pressure3,
            surface_type0,
            surface_type1,
            surface_type2,
            surface_type3,
        ) = struct.unpack_from(cls.STRUCT_FMT, b)

        return cls(
            speed=speed,
            throttle=throttle,
            steer=steer,
            brake=brake,
            clutch=clutch,
            gear=gear,
            engine_rpm=engine_rpm,
            drs=drs,
            rev_lights_percent=rev_lights_percent,
            rev_lights_bit_value=rev_lights_bit_value,
            brakes_temperature=(
                brakes_temperature0,
                brakes_temperature1,
                brakes_temperature2,
                brakes_temperature3,
            ),
            tyres_surface_temperature=(
                tyres_surface_temperature0,
                tyres_surface_temperature1,
                tyres_surface_temperature2,
                tyres_surface_temperature3,
            ),
            tyres_inner_temperature=(
                tyres_inner_temperature0,
                tyres_inner_temperature1,
                tyres_inner_temperature2,
                tyres_inner_temperature3,
            ),
            engine_temperature=engine_temperature,
            tyres_pressure=(
                tyres_pressure0,
                tyres_pressure1,
                tyres_pressure2,
                tyres_pressure3,
            ),
            surface_type=(
                surface_type0,
                surface_type1,
                surface_type2,
                surface_type3,
            ),
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.speed,
            self.throttle,
            self.steer,
            self.brake,
            self.clutch,
            self.gear,
            self.engine_rpm,
            self.drs,
            self.rev_lights_percent,
            self.rev_lights_bit_value,
            *self.brakes_temperature,
            *self.tyres_surface_temperature,
            *self.tyres_inner_temperature,
            self.engine_temperature,
            *self.tyres_pressure,
            *self.surface_type,
        )


@dataclass(frozen=True)
class PacketCarTelemetryData(BasePacket):
    header: PacketHeader
    car_telemetry_data: tuple[CarTelemetryData, ...]
    mfd_panel_index: int
    mfd_panel_index_secondary_player: int
    suggested_gear: int

    SIZE: ClassVar[int] = PacketHeader.SIZE + CarTelemetryData.SIZE * 22 + 3

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketCarTelemetryData", bytes]:
        data = cls._require_bytes(data, CarTelemetryData.SIZE * 22 + 3)

        car_telemetry_data = []
        offset = 0
        for _ in range(22):
            car_data = CarTelemetryData.from_bytes(
                data[offset : offset + CarTelemetryData.SIZE]
            )
            car_telemetry_data.append(car_data)
            offset += CarTelemetryData.SIZE

        (mfd_panel_index, mfd_panel_index_secondary_player, suggested_gear) = (
            struct.unpack_from(_ENDIAN + "3B", data[offset : offset + 3])
        )

        return cls(
            header=header,
            car_telemetry_data=tuple(car_telemetry_data),
            mfd_panel_index=mfd_panel_index,
            mfd_panel_index_secondary_player=mfd_panel_index_secondary_player,
            suggested_gear=suggested_gear,
        ), data[offset + 3 :]

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        for telemetry in self.car_telemetry_data:
            b += telemetry.to_bytes()
        b += struct.pack(
            _ENDIAN + "3B",
            self.mfd_panel_index,
            self.mfd_panel_index_secondary_player,
            self.suggested_gear,
        )
        return b
