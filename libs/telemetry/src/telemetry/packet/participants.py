import struct
from dataclasses import dataclass
from typing import ClassVar

from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class LiveryColour:
    red: int
    green: int
    blue: int

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "3B"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "LiveryColour":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        r, g, bl = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])
        return cls(red=r, green=g, blue=bl)

    def to_bytes(self) -> bytes:
        return struct.pack(self.STRUCT_FMT, self.red, self.green, self.blue)


@dataclass(frozen=True)
class ParticipantData:
    ai_controlled: int
    driver_id: int
    network_id: int
    team_id: int
    my_team: int
    race_number: int
    nationality: int
    name: str
    your_telemetry: int
    show_online_names: int
    tech_level: int
    platform: int
    num_colours: int
    livery_colours: list[LiveryColour]

    # 7 uint8, 32s, 2B, H, 2B, 12B
    STRUCT_FMT: ClassVar[str] = _ENDIAN + "7B32s2BH2B12B"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "ParticipantData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        unpacked = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])
        (
            ai,
            driverId,
            networkId,
            teamId,
            myTeam,
            raceNumber,
            nationality,
            name_bytes,
            yourTelemetry,
            showOnlineNames,
            techLevel,
            platform,
            numColours,
            *col_bytes,
        ) = unpacked

        # decode name (utf-8), strip trailing nulls
        name = name_bytes.split(b"\x00", 1)[0].decode("utf-8", errors="replace")

        # col_bytes contains 12 integers for 4 colours
        livery = []
        for i in range(0, 12, 3):
            r, g, bl = col_bytes[i : i + 3]
            livery.append(LiveryColour(red=r, green=g, blue=bl))

        return cls(
            ai_controlled=ai,
            driver_id=driverId,
            network_id=networkId,
            team_id=teamId,
            my_team=myTeam,
            race_number=raceNumber,
            nationality=nationality,
            name=name,
            your_telemetry=yourTelemetry,
            show_online_names=showOnlineNames,
            tech_level=techLevel,
            platform=platform,
            num_colours=numColours,
            livery_colours=livery,
        )

    def to_bytes(self) -> bytes:
        name_b = self.name.encode("utf-8")
        if len(name_b) >= 32:
            # truncate and ensure null-termination behavior similar to C-style
            name_b = name_b[:31] + b"\x00"
        name_b = name_b.ljust(32, b"\x00")

        col_flat = []
        # ensure exactly 4 colours
        cols = self.livery_colours[:4]
        while len(cols) < 4:
            cols.append(LiveryColour(0, 0, 0))
        for c in cols:
            col_flat.extend([c.red, c.green, c.blue])

        packed = struct.pack(
            self.STRUCT_FMT,
            self.ai_controlled,
            self.driver_id,
            self.network_id,
            self.team_id,
            self.my_team,
            self.race_number,
            self.nationality,
            name_b,
            self.your_telemetry,
            self.show_online_names,
            self.tech_level,
            self.platform,
            self.num_colours,
            *col_flat,
        )
        return packed


@dataclass(frozen=True)
class PacketParticipantsData:
    header: PacketHeader
    num_active_cars: int
    participants: list[ParticipantData]

    SIZE: ClassVar[int] = PacketHeader.SIZE + 1 + 22 * ParticipantData.SIZE

    @classmethod
    def from_bytes(cls, b: bytes) -> "PacketParticipantsData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        header = PacketHeader.from_bytes(b)
        offset = PacketHeader.SIZE
        num_active = struct.unpack(_ENDIAN + "B", b[offset : offset + 1])[0]
        offset += 1
        parts = []
        for _ in range(22):
            pd = ParticipantData.from_bytes(b[offset : offset + ParticipantData.SIZE])
            parts.append(pd)
            offset += ParticipantData.SIZE
        return cls(header=header, num_active_cars=num_active, participants=parts)

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        b += struct.pack(_ENDIAN + "B", self.num_active_cars)
        for p in self.participants:
            b += p.to_bytes()
        return b
