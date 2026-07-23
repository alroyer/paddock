import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"

MAX_LAPS = 50
MAX_CARS = 22


@dataclass(frozen=True)
class PacketLapPositionsData(BasePacket):
    num_laps: int
    lap_start: int
    position_for_vehicle_idx: tuple[tuple[int, ...], ...]

    SIZE: ClassVar[int] = PacketHeader.SIZE + 2 + MAX_LAPS * MAX_CARS

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketLapPositionsData", bytes]:
        data = cls._require_bytes(data, 2 + MAX_LAPS * MAX_CARS)

        offset = 0
        num_laps, lap_start = struct.unpack_from(_ENDIAN + "2B", data, offset)
        offset += 2

        rows = []
        for _ in range(MAX_LAPS):
            row = struct.unpack_from(_ENDIAN + f"{MAX_CARS}B", data, offset)
            rows.append(row)
            offset += MAX_CARS

        return cls(
            header=header,
            num_laps=num_laps,
            lap_start=lap_start,
            position_for_vehicle_idx=tuple(rows),
        ), data[offset:]

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        b += struct.pack(_ENDIAN + "2B", self.num_laps, self.lap_start)
        for row in self.position_for_vehicle_idx:
            b += struct.pack(_ENDIAN + f"{MAX_CARS}B", *row)
        return b

    def __post_init__(self) -> None:
        if self.header.packet_id != 15:
            raise ValueError(
                f"Invalid packet_id for PacketLapPositionsData: {self.header.packet_id}"
            )
