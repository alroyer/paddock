import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class LobbyInfoData:
    ai_controlled: int
    team_id: int
    nationality: int
    platform: int
    name: str
    car_number: int
    your_telemetry: int
    show_online_names: int
    tech_level: int
    ready_status: int

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "4B32s3BHB"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "LobbyInfoData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        (
            ai_controlled,
            team_id,
            nationality,
            platform,
            name_b,
            car_number,
            your_telemetry,
            show_online_names,
            tech_level,
            ready_status,
        ) = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])

        name = name_b.split(b"\x00", 1)[0].decode("utf-8", errors="replace")

        return cls(
            ai_controlled=ai_controlled,
            team_id=team_id,
            nationality=nationality,
            platform=platform,
            name=name,
            car_number=car_number,
            your_telemetry=your_telemetry,
            show_online_names=show_online_names,
            tech_level=tech_level,
            ready_status=ready_status,
        )

    def to_bytes(self) -> bytes:
        name_b = self.name.encode("utf-8")
        if len(name_b) >= 32:
            name_b = name_b[:31] + b"\x00"
        name_b = name_b.ljust(32, b"\x00")
        return struct.pack(
            self.STRUCT_FMT,
            self.ai_controlled,
            self.team_id,
            self.nationality,
            self.platform,
            name_b,
            self.car_number,
            self.your_telemetry,
            self.show_online_names,
            self.tech_level,
            self.ready_status,
        )


@dataclass(frozen=True)
class PacketLobbyInfoData(BasePacket):
    header: PacketHeader
    num_players: int
    lobby_players: list[LobbyInfoData]

    SIZE: ClassVar[int] = PacketHeader.SIZE + 1 + 22 * LobbyInfoData.SIZE

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketLobbyInfoData", bytes]:
        data = cls._require_bytes(data, 1 + 22 * LobbyInfoData.SIZE)
        offset = 0
        num_players = struct.unpack(_ENDIAN + "B", data[offset : offset + 1])[0]
        offset += 1
        arr = []
        for _ in range(22):
            li = LobbyInfoData.from_bytes(data[offset : offset + LobbyInfoData.SIZE])
            arr.append(li)
            offset += LobbyInfoData.SIZE
        return cls(header=header, num_players=num_players, lobby_players=arr), data[
            offset:
        ]

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        b += struct.pack(_ENDIAN + "B", self.num_players)
        for p in self.lobby_players:
            b += p.to_bytes()
        return b
