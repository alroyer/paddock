import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class TyreSetData:
    actual_tyre_compound: int
    visual_tyre_compound: int
    wear: int
    available: int
    recommended_session: int
    life_span: int
    usable_life: int
    lap_delta_time: int
    fitted: int

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "7BhB"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "TyreSetData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        (
            actual_tyre_compound,
            visual_tyre_compound,
            wear,
            available,
            recommended_session,
            life_span,
            usable_life,
            lap_delta_time,
            fitted,
        ) = struct.unpack_from(cls.STRUCT_FMT, b)
        return cls(
            actual_tyre_compound=actual_tyre_compound,
            visual_tyre_compound=visual_tyre_compound,
            wear=wear,
            available=available,
            recommended_session=recommended_session,
            life_span=life_span,
            usable_life=usable_life,
            lap_delta_time=lap_delta_time,
            fitted=fitted,
        )

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.actual_tyre_compound,
            self.visual_tyre_compound,
            self.wear,
            self.available,
            self.recommended_session,
            self.life_span,
            self.usable_life,
            self.lap_delta_time,
            self.fitted,
        )


@dataclass(frozen=True)
class PacketTyreSetsData(BasePacket):
    header: PacketHeader
    car_idx: int
    tyre_set_data: tuple[TyreSetData, ...]
    fitted_idx: int

    SIZE: ClassVar[int] = PacketHeader.SIZE + 1 + TyreSetData.SIZE * 20 + 1

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketTyreSetsData", bytes]:
        data = cls._require_bytes(data, 1 + TyreSetData.SIZE * 20 + 1)

        offset = 0
        car_idx = struct.unpack_from(_ENDIAN + "B", data[offset : offset + 1])[0]
        offset += 1

        tyre_sets = []
        for _ in range(20):
            tyre_set = TyreSetData.from_bytes(data[offset : offset + TyreSetData.SIZE])
            tyre_sets.append(tyre_set)
            offset += TyreSetData.SIZE

        fitted_idx = struct.unpack_from(_ENDIAN + "B", data[offset : offset + 1])[0]

        return cls(
            header=header,
            car_idx=car_idx,
            tyre_set_data=tuple(tyre_sets),
            fitted_idx=fitted_idx,
        ), data[offset + 1 :]

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        b += struct.pack(_ENDIAN + "B", self.car_idx)
        for tyre_set in self.tyre_set_data:
            b += tyre_set.to_bytes()
        b += struct.pack(_ENDIAN + "B", self.fitted_idx)
        return b

    def __post_init__(self) -> None:
        if self.header.packet_id != 12:
            raise ValueError(
                f"Invalid packet_id for PacketTyreSetsData: {self.header.packet_id}"
            )
