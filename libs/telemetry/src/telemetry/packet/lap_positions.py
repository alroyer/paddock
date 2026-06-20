import struct
from dataclasses import dataclass
from typing import ClassVar

from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"

MAX_LAPS = 50
MAX_CARS = 22


@dataclass(frozen=True)
class PacketLapPositionsData:
    header: PacketHeader
    num_laps: int
    lap_start: int
    position_for_vehicle_idx: tuple[tuple[int, ...], ...]

    SIZE: ClassVar[int] = PacketHeader.SIZE + 2 + MAX_LAPS * MAX_CARS

    @classmethod
    def from_bytes(cls, b: bytes) -> "PacketLapPositionsData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")

        header = PacketHeader.from_bytes(b[: PacketHeader.SIZE])
        offset = PacketHeader.SIZE
        num_laps, lap_start = struct.unpack_from(_ENDIAN + "2B", b, offset)
        offset += 2

        rows = []
        for _ in range(MAX_LAPS):
            row = struct.unpack_from(_ENDIAN + f"{MAX_CARS}B", b, offset)
            rows.append(row)
            offset += MAX_CARS

        return cls(
            header=header,
            num_laps=num_laps,
            lap_start=lap_start,
            position_for_vehicle_idx=tuple(rows),
        )

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        b += struct.pack(_ENDIAN + "2B", self.num_laps, self.lap_start)
        for row in self.position_for_vehicle_idx:
            b += struct.pack(_ENDIAN + f"{MAX_CARS}B", *row)
        return b
