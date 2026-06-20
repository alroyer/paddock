import struct
from dataclasses import dataclass
from typing import ClassVar

from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class FinalClassificationData:
    position: int
    num_laps: int
    grid_position: int
    points: int
    num_pit_stops: int
    result_status: int
    result_reason: int
    best_lap_time_in_ms: int
    total_race_time: float
    penalties_time: int
    num_penalties: int
    num_tyre_stints: int
    tyre_stints_actual: list[int]
    tyre_stints_visual: list[int]
    tyre_stints_end_laps: list[int]

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "7BI d 3B 8B 8B 8B".replace(" ", "")
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "FinalClassificationData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        unpacked = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])
        (
            position,
            num_laps,
            grid_position,
            points,
            num_pit_stops,
            result_status,
            result_reason,
            best_lap_time_in_ms,
            total_race_time,
            penalties_time,
            num_penalties,
            num_tyre_stints,
            *rest,
        ) = unpacked

        tyre_actual = list(rest[0:8])
        tyre_visual = list(rest[8:16])
        tyre_end_laps = list(rest[16:24])

        return cls(
            position=position,
            num_laps=num_laps,
            grid_position=grid_position,
            points=points,
            num_pit_stops=num_pit_stops,
            result_status=result_status,
            result_reason=result_reason,
            best_lap_time_in_ms=best_lap_time_in_ms,
            total_race_time=total_race_time,
            penalties_time=penalties_time,
            num_penalties=num_penalties,
            num_tyre_stints=num_tyre_stints,
            tyre_stints_actual=tyre_actual,
            tyre_stints_visual=tyre_visual,
            tyre_stints_end_laps=tyre_end_laps,
        )

    def to_bytes(self) -> bytes:
        flat = []
        flat.extend(self.tyre_stints_actual[:8])
        while len(flat) < 8:
            flat.append(0)
        visual = self.tyre_stints_visual[:8]
        while len(visual) < 8:
            visual.append(0)
        endlaps = self.tyre_stints_end_laps[:8]
        while len(endlaps) < 8:
            endlaps.append(0)

        return struct.pack(
            self.STRUCT_FMT,
            self.position,
            self.num_laps,
            self.grid_position,
            self.points,
            self.num_pit_stops,
            self.result_status,
            self.result_reason,
            self.best_lap_time_in_ms,
            self.total_race_time,
            self.penalties_time,
            self.num_penalties,
            self.num_tyre_stints,
            *self.tyre_stints_actual[:8],
            *self.tyre_stints_visual[:8],
            *self.tyre_stints_end_laps[:8],
        )


@dataclass(frozen=True)
class PacketFinalClassificationData:
    header: PacketHeader
    num_cars: int
    classification_data: list[FinalClassificationData]

    SIZE: ClassVar[int] = PacketHeader.SIZE + 1 + 22 * FinalClassificationData.SIZE

    @classmethod
    def from_bytes(cls, b: bytes) -> "PacketFinalClassificationData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        header = PacketHeader.from_bytes(b)
        offset = PacketHeader.SIZE
        num_cars = struct.unpack(_ENDIAN + "B", b[offset : offset + 1])[0]
        offset += 1
        arr = []
        for _ in range(22):
            fc = FinalClassificationData.from_bytes(
                b[offset : offset + FinalClassificationData.SIZE]
            )
            arr.append(fc)
            offset += FinalClassificationData.SIZE
        return cls(header=header, num_cars=num_cars, classification_data=arr)

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        b += struct.pack(_ENDIAN + "B", self.num_cars)
        for fc in self.classification_data:
            b += fc.to_bytes()
        return b
