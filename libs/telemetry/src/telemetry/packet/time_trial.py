import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class TimeTrialDataSet:
    car_idx: int
    team_id: int
    lap_time_in_ms: int
    sector1_time_in_ms: int
    sector2_time_in_ms: int
    sector3_time_in_ms: int
    traction_control: int
    gearbox_assist: int
    anti_lock_brakes: int
    equal_car_performance: int
    custom_setup: int
    valid: int

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "2B4I6B"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, data: bytes) -> "TimeTrialDataSet":
        if len(data) < cls.SIZE:
            raise ValueError(
                f"buffer too small: need {cls.SIZE} bytes, got {len(data)}"
            )
        (
            car_idx,
            team_id,
            lap_time_in_ms,
            sector1_time_in_ms,
            sector2_time_in_ms,
            sector3_time_in_ms,
            traction_control,
            gearbox_assist,
            anti_lock_brakes,
            equal_car_performance,
            custom_setup,
            valid,
        ) = struct.unpack_from(cls.STRUCT_FMT, data)
        return cls(
            car_idx=car_idx,
            team_id=team_id,
            lap_time_in_ms=lap_time_in_ms,
            sector1_time_in_ms=sector1_time_in_ms,
            sector2_time_in_ms=sector2_time_in_ms,
            sector3_time_in_ms=sector3_time_in_ms,
            traction_control=traction_control,
            gearbox_assist=gearbox_assist,
            anti_lock_brakes=anti_lock_brakes,
            equal_car_performance=equal_car_performance,
            custom_setup=custom_setup,
            valid=valid,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.car_idx,
            self.team_id,
            self.lap_time_in_ms,
            self.sector1_time_in_ms,
            self.sector2_time_in_ms,
            self.sector3_time_in_ms,
            self.traction_control,
            self.gearbox_assist,
            self.anti_lock_brakes,
            self.equal_car_performance,
            self.custom_setup,
            self.valid,
        )


@dataclass(frozen=True)
class PacketTimeTrialData(BasePacket):
    player_session_best_data_set: TimeTrialDataSet
    personal_best_data_set: TimeTrialDataSet
    rival_data_set: TimeTrialDataSet

    SIZE: ClassVar[int] = PacketHeader.SIZE + TimeTrialDataSet.SIZE * 3

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketTimeTrialData", bytes]:
        data = cls._require_bytes(data, TimeTrialDataSet.SIZE * 3)

        offset = 0
        player_session_best_data_set = TimeTrialDataSet.from_bytes(
            data[offset : offset + TimeTrialDataSet.SIZE]
        )
        offset += TimeTrialDataSet.SIZE
        personal_best_data_set = TimeTrialDataSet.from_bytes(
            data[offset : offset + TimeTrialDataSet.SIZE]
        )
        offset += TimeTrialDataSet.SIZE
        rival_data_set = TimeTrialDataSet.from_bytes(
            data[offset : offset + TimeTrialDataSet.SIZE]
        )

        return cls(
            header=header,
            player_session_best_data_set=player_session_best_data_set,
            personal_best_data_set=personal_best_data_set,
            rival_data_set=rival_data_set,
        ), data[offset + TimeTrialDataSet.SIZE :]

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        b += self.player_session_best_data_set.to_bytes()
        b += self.personal_best_data_set.to_bytes()
        b += self.rival_data_set.to_bytes()
        return b

    def __post_init__(self) -> None:
        if self.header.packet_id != 14:
            raise ValueError(
                f"Invalid packet_id for PacketTimeTrialData: {self.header.packet_id}"
            )
