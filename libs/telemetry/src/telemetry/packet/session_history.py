import struct
from dataclasses import dataclass
from typing import ClassVar

from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class LapHistoryData:
    lap_time_in_ms: int
    sector1_time_ms_part: int
    sector1_time_minutes_part: int
    sector2_time_ms_part: int
    sector2_time_minutes_part: int
    sector3_time_ms_part: int
    sector3_time_minutes_part: int
    lap_valid_bit_flags: int

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "IHBHBHBB"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "LapHistoryData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        (
            lap_time_in_ms,
            sector1_time_ms_part,
            sector1_time_minutes_part,
            sector2_time_ms_part,
            sector2_time_minutes_part,
            sector3_time_ms_part,
            sector3_time_minutes_part,
            lap_valid_bit_flags,
        ) = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])
        return cls(
            lap_time_in_ms=lap_time_in_ms,
            sector1_time_ms_part=sector1_time_ms_part,
            sector1_time_minutes_part=sector1_time_minutes_part,
            sector2_time_ms_part=sector2_time_ms_part,
            sector2_time_minutes_part=sector2_time_minutes_part,
            sector3_time_ms_part=sector3_time_ms_part,
            sector3_time_minutes_part=sector3_time_minutes_part,
            lap_valid_bit_flags=lap_valid_bit_flags,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.lap_time_in_ms,
            self.sector1_time_ms_part,
            self.sector1_time_minutes_part,
            self.sector2_time_ms_part,
            self.sector2_time_minutes_part,
            self.sector3_time_ms_part,
            self.sector3_time_minutes_part,
            self.lap_valid_bit_flags,
        )


@dataclass(frozen=True)
class TyreStintHistoryData:
    end_lap: int
    tyre_actual_compound: int
    tyre_visual_compound: int

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "3B"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "TyreStintHistoryData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        end_lap, tyre_actual_compound, tyre_visual_compound = struct.unpack(
            cls.STRUCT_FMT, b[: cls.SIZE]
        )
        return cls(
            end_lap=end_lap,
            tyre_actual_compound=tyre_actual_compound,
            tyre_visual_compound=tyre_visual_compound,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.end_lap,
            self.tyre_actual_compound,
            self.tyre_visual_compound,
        )


@dataclass(frozen=True)
class PacketSessionHistoryData:
    header: PacketHeader
    car_idx: int
    num_laps: int
    num_tyre_stints: int
    best_lap_time_lap_num: int
    best_sector1_lap_num: int
    best_sector2_lap_num: int
    best_sector3_lap_num: int
    lap_history_data: list[LapHistoryData]
    tyre_stints_history_data: list[TyreStintHistoryData]

    SIZE: ClassVar[int] = (
        PacketHeader.SIZE
        + 7
        + 100 * LapHistoryData.SIZE
        + 8 * TyreStintHistoryData.SIZE
    )

    @classmethod
    def from_bytes(cls, b: bytes) -> "PacketSessionHistoryData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        header = PacketHeader.from_bytes(b)
        offset = PacketHeader.SIZE
        (
            car_idx,
            num_laps,
            num_tyre_stints,
            best_lap_time_lap_num,
            best_sector1_lap_num,
            best_sector2_lap_num,
            best_sector3_lap_num,
        ) = struct.unpack(_ENDIAN + "7B", b[offset : offset + 7])
        offset += 7

        lap_history = []
        for _ in range(100):
            lh = LapHistoryData.from_bytes(b[offset : offset + LapHistoryData.SIZE])
            lap_history.append(lh)
            offset += LapHistoryData.SIZE

        tyre_history = []
        for _ in range(8):
            th = TyreStintHistoryData.from_bytes(
                b[offset : offset + TyreStintHistoryData.SIZE]
            )
            tyre_history.append(th)
            offset += TyreStintHistoryData.SIZE

        return cls(
            header=header,
            car_idx=car_idx,
            num_laps=num_laps,
            num_tyre_stints=num_tyre_stints,
            best_lap_time_lap_num=best_lap_time_lap_num,
            best_sector1_lap_num=best_sector1_lap_num,
            best_sector2_lap_num=best_sector2_lap_num,
            best_sector3_lap_num=best_sector3_lap_num,
            lap_history_data=lap_history,
            tyre_stints_history_data=tyre_history,
        )

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        b += struct.pack(
            _ENDIAN + "7B",
            self.car_idx,
            self.num_laps,
            self.num_tyre_stints,
            self.best_lap_time_lap_num,
            self.best_sector1_lap_num,
            self.best_sector2_lap_num,
            self.best_sector3_lap_num,
        )
        for lh in self.lap_history_data:
            b += lh.to_bytes()
        for th in self.tyre_stints_history_data:
            b += th.to_bytes()
        return b
