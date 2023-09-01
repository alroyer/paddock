import struct
from typing import Tuple, Union

from .event import PacketEventData
from .header import PacketHeader
from .lapdata import PacketLapData
from .motion import PacketMotionData
from .session import PacketSessionData


class InvalidData(Exception):
    pass


def _parse(
    data: bytes,
) -> Tuple[
    Union[PacketEventData, PacketLapData, PacketMotionData, PacketSessionData], bytes
]:
    header = PacketHeader(*struct.unpack('<HBBBBBQfIIBB', data[:29]))
    if header.packet_id == 3:
        packet_event, data = _parse_event(header, data[29:])
        return packet_event, data
    raise InvalidData()


def _parse_event(header: PacketHeader, data: bytes) -> Tuple[PacketEventData, bytes]:
    event_string_code = ''.join([chr(b) for b in struct.unpack('BBBB', data[:4])])
    if event_string_code == 'BUTN':
        buttons_event, data = _parse_buttons_event(header, data[5:])
        return buttons_event, data
    raise InvalidData()


def _parse_buttons_event(
    header: PacketHeader, data: bytes
) -> Tuple[PacketEventData, bytes]:
    pass


def parse(
    data: bytes,
) -> list[Union[PacketEventData, PacketLapData, PacketMotionData, PacketSessionData]]:
    packets = []
    while data:
        packet, data = _parse(data)
        packets.append(packet)
    return packets
