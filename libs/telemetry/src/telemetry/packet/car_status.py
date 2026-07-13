import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class CarStatusData:
    traction_control: int
    anti_lock_brakes: int
    fuel_mix: int
    front_brake_bias: int
    pit_limiter_status: int
    fuel_in_tank: float
    fuel_capacity: float
    fuel_remaining_laps: float
    max_rpm: int
    idle_rpm: int
    max_gears: int
    drs_allowed: int
    drs_activation_distance: int
    actual_tyre_compound: int
    visual_tyre_compound: int
    tyres_age_laps: int
    vehicle_fia_flags: int
    engine_power_ice: float
    engine_power_mguk: float
    ers_store_energy: float
    ers_deploy_mode: int
    ers_harvested_this_lap_mguk: float
    ers_harvested_this_lap_mguh: float
    ers_deployed_this_lap: float
    network_paused: int

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "5B3f2H2BH3Bb3fB3fB"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, data: bytes) -> "CarStatusData":
        if len(data) < cls.SIZE:
            raise ValueError(
                f"buffer too small: need {cls.SIZE} bytes, got {len(data)}"
            )
        (
            traction_control,
            anti_lock_brakes,
            fuel_mix,
            front_brake_bias,
            pit_limiter_status,
            fuel_in_tank,
            fuel_capacity,
            fuel_remaining_laps,
            max_rpm,
            idle_rpm,
            max_gears,
            drs_allowed,
            drs_activation_distance,
            actual_tyre_compound,
            visual_tyre_compound,
            tyres_age_laps,
            vehicle_fia_flags,
            engine_power_ice,
            engine_power_mguk,
            ers_store_energy,
            ers_deploy_mode,
            ers_harvested_this_lap_mguk,
            ers_harvested_this_lap_mguh,
            ers_deployed_this_lap,
            network_paused,
        ) = struct.unpack(cls.STRUCT_FMT, data[: cls.SIZE])

        return cls(
            traction_control=traction_control,
            anti_lock_brakes=anti_lock_brakes,
            fuel_mix=fuel_mix,
            front_brake_bias=front_brake_bias,
            pit_limiter_status=pit_limiter_status,
            fuel_in_tank=fuel_in_tank,
            fuel_capacity=fuel_capacity,
            fuel_remaining_laps=fuel_remaining_laps,
            max_rpm=max_rpm,
            idle_rpm=idle_rpm,
            max_gears=max_gears,
            drs_allowed=drs_allowed,
            drs_activation_distance=drs_activation_distance,
            actual_tyre_compound=actual_tyre_compound,
            visual_tyre_compound=visual_tyre_compound,
            tyres_age_laps=tyres_age_laps,
            vehicle_fia_flags=vehicle_fia_flags,
            engine_power_ice=engine_power_ice,
            engine_power_mguk=engine_power_mguk,
            ers_store_energy=ers_store_energy,
            ers_deploy_mode=ers_deploy_mode,
            ers_harvested_this_lap_mguk=ers_harvested_this_lap_mguk,
            ers_harvested_this_lap_mguh=ers_harvested_this_lap_mguh,
            ers_deployed_this_lap=ers_deployed_this_lap,
            network_paused=network_paused,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.traction_control,
            self.anti_lock_brakes,
            self.fuel_mix,
            self.front_brake_bias,
            self.pit_limiter_status,
            self.fuel_in_tank,
            self.fuel_capacity,
            self.fuel_remaining_laps,
            self.max_rpm,
            self.idle_rpm,
            self.max_gears,
            self.drs_allowed,
            self.drs_activation_distance,
            self.actual_tyre_compound,
            self.visual_tyre_compound,
            self.tyres_age_laps,
            self.vehicle_fia_flags,
            self.engine_power_ice,
            self.engine_power_mguk,
            self.ers_store_energy,
            self.ers_deploy_mode,
            self.ers_harvested_this_lap_mguk,
            self.ers_harvested_this_lap_mguh,
            self.ers_deployed_this_lap,
            self.network_paused,
        )


@dataclass(frozen=True)
class PacketCarStatusData(BasePacket):
    header: PacketHeader
    car_status_data: list[CarStatusData]

    SIZE: ClassVar[int] = PacketHeader.SIZE + 22 * CarStatusData.SIZE

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketCarStatusData", bytes]:
        data = cls._require_bytes(data, 22 * CarStatusData.SIZE)
        offset = 0
        arr = []
        for _ in range(22):
            cs = CarStatusData.from_bytes(data[offset : offset + CarStatusData.SIZE])
            arr.append(cs)
            offset += CarStatusData.SIZE
        return cls(header=header, car_status_data=arr), data[offset:]

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        for cs in self.car_status_data:
            b += cs.to_bytes()
        return b

    def __post_init__(self) -> None:
        if self.header.packet_id != 7:
            raise ValueError(
                f"Invalid packet_id for PacketCarStatusData: {self.header.packet_id}"
            )
