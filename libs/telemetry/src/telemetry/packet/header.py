import struct
from dataclasses import dataclass
from typing import ClassVar

from .constants import BYTES_ORDER


@dataclass(frozen=True)
class PacketHeader:
    packet_format: int
    game_year: int
    game_major_version: int
    game_minor_version: int
    packet_version: int
    packet_id: int
    session_uid: int
    session_time: float
    frame_identifier: int
    overall_frame_identifier: int
    player_car_index: int
    secondary_player_car_index: int

    STRUCT_FMT: ClassVar[str] = (
        "<H5BQfII2B" if BYTES_ORDER == "little" else ">H5BQfII2B"
    )
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def parse(cls, data: bytes) -> tuple["PacketHeader", bytes]:
        if len(data) < cls.SIZE:
            raise ValueError(
                f"buffer too small: need {cls.SIZE} bytes, got {len(data)}"
            )
        (
            packet_format,
            game_year,
            game_major_version,
            game_minor_version,
            packet_version,
            packet_id,
            session_uid,
            session_time,
            frame_identifier,
            overall_frame_identifier,
            player_car_index,
            secondary_player_car_index,
        ) = struct.unpack(cls.STRUCT_FMT, data[: cls.SIZE])

        header = cls(
            packet_format=packet_format,
            game_year=game_year,
            game_major_version=game_major_version,
            game_minor_version=game_minor_version,
            packet_version=packet_version,
            packet_id=packet_id,
            session_uid=session_uid,
            session_time=session_time,
            frame_identifier=frame_identifier,
            overall_frame_identifier=overall_frame_identifier,
            player_car_index=player_car_index,
            secondary_player_car_index=secondary_player_car_index,
        )
        return header, data[cls.SIZE :]

    def to_bytes(self) -> bytes:
        return struct.pack(
            self.STRUCT_FMT,
            self.packet_format,
            self.game_year,
            self.game_major_version,
            self.game_minor_version,
            self.packet_version,
            self.packet_id,
            self.session_uid,
            self.session_time,
            self.frame_identifier,
            self.overall_frame_identifier,
            self.player_car_index,
            self.secondary_player_car_index,
        )
