import struct
from dataclasses import dataclass
from typing import ClassVar

from .base import BasePacket
from .constants import BYTES_ORDER
from .header import PacketHeader

_ENDIAN = "<" if BYTES_ORDER == "little" else ">"


@dataclass(frozen=True)
class CarDamageData:
    tyres_wear: list[float]
    tyres_damage: list[int]
    brakes_damage: list[int]
    tyre_blisters: list[int]
    front_left_wing_damage: int
    front_right_wing_damage: int
    rear_wing_damage: int
    floor_damage: int
    diffuser_damage: int
    sidepod_damage: int
    drs_fault: int
    ers_fault: int
    gear_box_damage: int
    engine_damage: int
    engine_mguh_wear: int
    engine_es_wear: int
    engine_ce_wear: int
    engine_ice_wear: int
    engine_mguk_wear: int
    engine_tc_wear: int
    engine_blown: int
    engine_seized: int

    STRUCT_FMT: ClassVar[str] = _ENDIAN + "4f30B"
    SIZE: ClassVar[int] = struct.calcsize(STRUCT_FMT)

    @classmethod
    def from_bytes(cls, b: bytes) -> "CarDamageData":
        if len(b) < cls.SIZE:
            raise ValueError(f"buffer too small: need {cls.SIZE} bytes, got {len(b)}")
        unpacked = struct.unpack(cls.STRUCT_FMT, b[: cls.SIZE])
        tyres_wear = list(unpacked[0:4])
        bytes_start = 4
        uints = list(unpacked[bytes_start:])

        tyres_damage = uints[0:4]
        brakes_damage = uints[4:8]
        tyre_blisters = uints[8:12]
        rest = uints[12:]

        (
            front_left_wing_damage,
            front_right_wing_damage,
            rear_wing_damage,
            floor_damage,
            diffuser_damage,
            sidepod_damage,
            drs_fault,
            ers_fault,
            gear_box_damage,
            engine_damage,
            engine_mguh_wear,
            engine_es_wear,
            engine_ce_wear,
            engine_ice_wear,
            engine_mguk_wear,
            engine_tc_wear,
            engine_blown,
            engine_seized,
        ) = rest

        return cls(
            tyres_wear=tyres_wear,
            tyres_damage=tyres_damage,
            brakes_damage=brakes_damage,
            tyre_blisters=tyre_blisters,
            front_left_wing_damage=front_left_wing_damage,
            front_right_wing_damage=front_right_wing_damage,
            rear_wing_damage=rear_wing_damage,
            floor_damage=floor_damage,
            diffuser_damage=diffuser_damage,
            sidepod_damage=sidepod_damage,
            drs_fault=drs_fault,
            ers_fault=ers_fault,
            gear_box_damage=gear_box_damage,
            engine_damage=engine_damage,
            engine_mguh_wear=engine_mguh_wear,
            engine_es_wear=engine_es_wear,
            engine_ce_wear=engine_ce_wear,
            engine_ice_wear=engine_ice_wear,
            engine_mguk_wear=engine_mguk_wear,
            engine_tc_wear=engine_tc_wear,
            engine_blown=engine_blown,
            engine_seized=engine_seized,
        )

    def to_bytes(self) -> bytes:
        flat_uints = []
        flat_uints.extend(self.tyres_damage[:4])
        while len(flat_uints) < 4:
            flat_uints.append(0)
        flat_uints.extend(self.brakes_damage[:4])
        while len(flat_uints) < 8:
            flat_uints.append(0)
        flat_uints.extend(self.tyre_blisters[:4])
        while len(flat_uints) < 12:
            flat_uints.append(0)

        rest = [
            self.front_left_wing_damage,
            self.front_right_wing_damage,
            self.rear_wing_damage,
            self.floor_damage,
            self.diffuser_damage,
            self.sidepod_damage,
            self.drs_fault,
            self.ers_fault,
            self.gear_box_damage,
            self.engine_damage,
            self.engine_mguh_wear,
            self.engine_es_wear,
            self.engine_ce_wear,
            self.engine_ice_wear,
            self.engine_mguk_wear,
            self.engine_tc_wear,
            self.engine_blown,
            self.engine_seized,
        ]

        flat_uints.extend(rest)

        return struct.pack(
            self.STRUCT_FMT,
            *self.tyres_wear[:4],
            *flat_uints,
        )


@dataclass(frozen=True)
class PacketCarDamageData(BasePacket):
    header: PacketHeader
    car_damage_data: list[CarDamageData]

    SIZE: ClassVar[int] = PacketHeader.SIZE + 22 * CarDamageData.SIZE

    @classmethod
    def parse(
        cls, header: PacketHeader, data: bytes
    ) -> tuple["PacketCarDamageData", bytes]:
        car_damage_data, remaining = cls._parse_items(
            data, CarDamageData.SIZE, 22, CarDamageData.from_bytes
        )
        return cls(header=header, car_damage_data=car_damage_data), remaining

    def to_bytes(self) -> bytes:
        b = self.header.to_bytes()
        for cd in self.car_damage_data:
            b += cd.to_bytes()
        return b

    def __post_init__(self) -> None:
        if self.header.packet_id != 10:
            raise ValueError(
                f"Invalid packet_id for PacketCarDamageData: {self.header.packet_id}"
            )
