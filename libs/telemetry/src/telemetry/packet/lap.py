import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader


@dataclass(frozen=True)
class LapData:
    last_lap_time_in_ms: int
    current_lap_time_in_ms: int
    sector1_time_ms_part: int
    sector1_time_minutes_part: int
    sector2_time_ms_part: int
    sector2_time_minutes_part: int
    delta_to_car_in_front_ms_part: int
    delta_to_car_in_front_minutes_part: int
    delta_to_race_leader_ms_part: int
    delta_to_race_leader_minutes_part: int
    lap_distance: float
    total_distance: float
    safety_car_delta: float
    car_position: int
    current_lap_num: int
    pit_status: int
    num_pit_stops: int
    sector: int
    current_lap_invalid: int
    penalties: int
    total_warnings: int
    corner_cutting_warnings: int
    num_unserved_drive_through_pens: int
    num_unserved_stop_go_pens: int
    grid_position: int
    driver_status: int
    result_status: int
    pit_lane_timer_active: int
    pit_lane_time_in_lane_in_ms: int
    pit_stop_timer_in_ms: int
    pit_stop_should_serve_pen: int
    speed_trap_fastest_speed: float
    speed_trap_fastest_lap: int

    STRUCT_FMT: ClassVar[str] = (
        "<IIHBHBHBHBfff15BHHBfB"
        if BYTES_ORDER == "little"
        else ">IIHBHBHBHBfff15BHHBfB"
    )
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "LapData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        (
            last_lap_time_in_ms,
            current_lap_time_in_ms,
            sector1_time_ms_part,
            sector1_time_minutes_part,
            sector2_time_ms_part,
            sector2_time_minutes_part,
            delta_to_car_in_front_ms_part,
            delta_to_car_in_front_minutes_part,
            delta_to_race_leader_ms_part,
            delta_to_race_leader_minutes_part,
            lap_distance,
            total_distance,
            safety_car_delta,
            car_position,
            current_lap_num,
            pit_status,
            num_pit_stops,
            sector,
            current_lap_invalid,
            penalties,
            total_warnings,
            corner_cutting_warnings,
            num_unserved_drive_through_pens,
            num_unserved_stop_go_pens,
            grid_position,
            driver_status,
            result_status,
            pit_lane_timer_active,
            pit_lane_time_in_lane_in_ms,
            pit_stop_timer_in_ms,
            pit_stop_should_serve_pen,
            speed_trap_fastest_speed,
            speed_trap_fastest_lap,
        ) = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])
        return cls(
            last_lap_time_in_ms=last_lap_time_in_ms,
            current_lap_time_in_ms=current_lap_time_in_ms,
            sector1_time_ms_part=sector1_time_ms_part,
            sector1_time_minutes_part=sector1_time_minutes_part,
            sector2_time_ms_part=sector2_time_ms_part,
            sector2_time_minutes_part=sector2_time_minutes_part,
            delta_to_car_in_front_ms_part=delta_to_car_in_front_ms_part,
            delta_to_car_in_front_minutes_part=delta_to_car_in_front_minutes_part,
            delta_to_race_leader_ms_part=delta_to_race_leader_ms_part,
            delta_to_race_leader_minutes_part=delta_to_race_leader_minutes_part,
            lap_distance=lap_distance,
            total_distance=total_distance,
            safety_car_delta=safety_car_delta,
            car_position=car_position,
            current_lap_num=current_lap_num,
            pit_status=pit_status,
            num_pit_stops=num_pit_stops,
            sector=sector,
            current_lap_invalid=current_lap_invalid,
            penalties=penalties,
            total_warnings=total_warnings,
            corner_cutting_warnings=corner_cutting_warnings,
            num_unserved_drive_through_pens=num_unserved_drive_through_pens,
            num_unserved_stop_go_pens=num_unserved_stop_go_pens,
            grid_position=grid_position,
            driver_status=driver_status,
            result_status=result_status,
            pit_lane_timer_active=pit_lane_timer_active,
            pit_lane_time_in_lane_in_ms=pit_lane_time_in_lane_in_ms,
            pit_stop_timer_in_ms=pit_stop_timer_in_ms,
            pit_stop_should_serve_pen=pit_stop_should_serve_pen,
            speed_trap_fastest_speed=speed_trap_fastest_speed,
            speed_trap_fastest_lap=speed_trap_fastest_lap,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.last_lap_time_in_ms,
            self.current_lap_time_in_ms,
            self.sector1_time_ms_part,
            self.sector1_time_minutes_part,
            self.sector2_time_ms_part,
            self.sector2_time_minutes_part,
            self.delta_to_car_in_front_ms_part,
            self.delta_to_car_in_front_minutes_part,
            self.delta_to_race_leader_ms_part,
            self.delta_to_race_leader_minutes_part,
            self.lap_distance,
            self.total_distance,
            self.safety_car_delta,
            self.car_position,
            self.current_lap_num,
            self.pit_status,
            self.num_pit_stops,
            self.sector,
            self.current_lap_invalid,
            self.penalties,
            self.total_warnings,
            self.corner_cutting_warnings,
            self.num_unserved_drive_through_pens,
            self.num_unserved_stop_go_pens,
            self.grid_position,
            self.driver_status,
            self.result_status,
            self.pit_lane_timer_active,
            self.pit_lane_time_in_lane_in_ms,
            self.pit_stop_timer_in_ms,
            self.pit_stop_should_serve_pen,
            self.speed_trap_fastest_speed,
            self.speed_trap_fastest_lap,
        )


@dataclass(frozen=True)
class PacketLapData(BasePacket):
    header: PacketHeader
    lap_data: list[LapData]
    time_trial_pb_car_idx: int
    time_trial_rival_car_idx: int

    SIZE: ClassVar[int] = PacketHeader.SIZE + 22 * LapData.SIZE + 2

    @classmethod
    def parse(cls, header: PacketHeader, data: bytes) -> tuple["PacketLapData", bytes]:
        data = cls._require_bytes(data, 22 * LapData.SIZE + 2)
        offset = 0
        lap_data = []
        for _ in range(22):
            lap = LapData.from_bytes(data[offset : offset + LapData.SIZE])
            lap_data.append(lap)
            offset += LapData.SIZE
        time_trial_pb_car_idx, time_trial_rival_car_idx = struct.unpack(
            "<BB" if BYTES_ORDER == "little" else ">BB",
            data[offset : offset + 2],
        )
        return cls(
            header=header,
            lap_data=lap_data,
            time_trial_pb_car_idx=time_trial_pb_car_idx,
            time_trial_rival_car_idx=time_trial_rival_car_idx,
        ), data[offset + 2 :]

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        for lap in self.lap_data:
            b += lap.to_bytes()
        b += struct.pack(
            "<BB" if BYTES_ORDER == "little" else ">BB",
            self.time_trial_pb_car_idx,
            self.time_trial_rival_car_idx,
        )
        return b


__all__ = ["LapData", "PacketLapData"]
