import struct
from dataclasses import dataclass
from typing import ClassVar, cast

from .base import BasePacket
from .constants import BYTES_ORDER, EVENT_CODES
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class EventDataDetails:
    """Opaque container for event union data. Stored as fixed-size bytes.

    Helpers are provided to construct common variants and to decode them.
    """

    raw: bytes

    SIZE: ClassVar[int] = 12

    @classmethod
    def from_bytes(cls, data: bytes) -> "EventDataDetails":
        if len(data) < cls.SIZE:
            raise ValueError(
                f"buffer too small: need {cls.SIZE} bytes, got {len(data)}"
            )
        return cls(raw=data[: cls.SIZE])

    def to_bytes(self) -> bytes:
        return self.raw.ljust(self.SIZE, b"\x00")

    @classmethod
    def from_fastest_lap(cls, vehicle_idx: int, lap_time: float) -> "EventDataDetails":
        packed = struct.pack(_ENDIAN + "Bf", vehicle_idx, lap_time)
        return cls(raw=packed)

    def as_fastest_lap(self):
        vehicle_idx, lap_time = struct.unpack(_ENDIAN + "Bf", self.raw[:5])
        return vehicle_idx, lap_time

    @classmethod
    def from_retirement(cls, vehicle_idx: int, reason: int) -> "EventDataDetails":
        packed = struct.pack(_ENDIAN + "BB", vehicle_idx, reason)
        return cls(raw=packed)

    def as_retirement(self):
        vehicle_idx, reason = struct.unpack(_ENDIAN + "BB", self.raw[:2])
        return vehicle_idx, reason

    @classmethod
    def from_speed_trap(
        cls,
        vehicle_idx: int,
        speed: float,
        is_overall: int,
        is_driver: int,
        fastest_vehicle_idx: int,
        fastest_speed: float,
    ) -> "EventDataDetails":
        packed = struct.pack(
            _ENDIAN + "BfBBBf",
            vehicle_idx,
            speed,
            is_overall,
            is_driver,
            fastest_vehicle_idx,
            fastest_speed,
        )
        return cls(raw=packed)

    def as_speed_trap(self):
        (
            vehicle_idx,
            speed,
            is_overall,
            is_driver,
            fastest_vehicle_idx,
            fastest_speed,
        ) = struct.unpack(_ENDIAN + "BfBBBf", self.raw[:12])
        return (
            vehicle_idx,
            speed,
            is_overall,
            is_driver,
            fastest_vehicle_idx,
            fastest_speed,
        )

    @classmethod
    def from_flashback(
        cls, frame_identifier: int, session_time: float
    ) -> "EventDataDetails":
        packed = struct.pack(_ENDIAN + "If", frame_identifier, session_time)
        return cls(raw=packed)

    def as_flashback(self):
        frame_identifier, session_time = struct.unpack(_ENDIAN + "If", self.raw[:8])
        return frame_identifier, session_time


@dataclass(frozen=True)
class PacketEventData(BasePacket):
    header: PacketHeader
    event_string_code: bytes
    event_details: EventDataDetails

    SIZE: ClassVar[int] = PacketHeader.SIZE + 4 + EventDataDetails.SIZE

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketEventData", bytes]:
        payload = cls._require_bytes(data, EventDataDetails.SIZE + 4)
        event_string_code, payload = cls._take_bytes(payload, 4)
        event_details_bytes, remaining = cls._take_bytes(payload, EventDataDetails.SIZE)
        event_details = EventDataDetails.from_bytes(event_details_bytes)
        return cls(
            header=header,
            event_string_code=event_string_code,
            event_details=event_details,
        ), remaining

    def to_bytes(self) -> bytes:
        data = self.header.to_bytes()
        code = self.event_string_code
        if isinstance(code, str):
            code = code.encode("ascii")
        if len(code) != 4:
            raise ValueError("event_string_code must be 4 bytes")
        data += code
        data += self.event_details.to_bytes()
        return data

    def event_name(self) -> str:
        raw_code = self.event_string_code
        if isinstance(raw_code, (bytes, bytearray)):
            try:
                code_str = raw_code.decode("ascii")
            except Exception:
                return "Unknown"
        else:
            code_str = cast(str, raw_code)
        return EVENT_CODES.get(code_str, "Unknown")
