import struct
from typing import Tuple, Union

from .event import Buttons, PacketEventData, SessionEnded, SessionStarted
from .header import PacketHeader
from .lapdata import PacketLapData
from .motion import PacketMotionData
from .participant import PacketParticipantsData
from .session import PacketSessionData


def _read(data: bytes, count: int) -> Tuple[bytes, bytes]:
    return data[:count], data[count:]


def _parse(data: bytes) -> Tuple[Union[PacketEventData, PacketLapData, PacketMotionData, PacketSessionData], bytes]:
    # 29 bytes
    header = PacketHeader(*struct.unpack('<HBBBBBQfIIBB', data[:29]))

    # TODO to be remove
    assert header.game_year == 23 and header.packet_format == 2023

    packet_handler = PACKET_HANDLER[header.packet_id]
    return packet_handler(header, data[29:])


def _parse_event_data(header: PacketHeader, data: bytes) -> Tuple[PacketEventData, bytes]:
    # 45 bytes
    event_data, remaining_data = _read(data, 45 - 29)
    event_string_code = ''.join([chr(b) for b in struct.unpack('<BBBB', event_data[:4])])
    event_handler = EVENT_HANDLER[event_string_code]
    return event_handler(header, event_string_code, event_data[4:]), remaining_data


def _parse_session_data(header: PacketHeader, data: bytes) -> Tuple[PacketSessionData, bytes]:
    # 644 bytes
    session_data, remaining_data = _read(data, 644 - 29)
    # TODO
    return PacketSessionData(), remaining_data


def _parse_participants_data(header: PacketHeader, data: bytes) -> Tuple[PacketParticipantsData, bytes]:
    # 1306 bytes
    participants_data, remaining_data = _read(data, 1306 - 29)
    # TODO
    return PacketParticipantsData(), remaining_data


def _parse_buttons_event(header: PacketHeader, event_string_code: str, data: bytes) -> PacketEventData:
    button_status = struct.unpack('<I', data[:4])[0]
    return PacketEventData(header, event_string_code, Buttons(button_status))


def _parse_session_started_event(header: PacketHeader, event_string_code: str, _: bytes) -> PacketEventData:
    return PacketEventData(header, event_string_code, SessionStarted())


def _parse_session_ended_event(header: PacketHeader, event_string_code: str, _: bytes) -> PacketEventData:
    return PacketEventData(header, event_string_code, SessionEnded())


PACKET_HANDLER = {
    1: _parse_session_data,
    3: _parse_event_data,
    4: _parse_participants_data,
}

EVENT_HANDLER = {
    'BUTN': _parse_buttons_event,
    'SSTA': _parse_session_started_event,
    'SEND': _parse_session_ended_event,
}


def parse(data: bytes) -> list[Union[PacketEventData, PacketLapData, PacketMotionData, PacketSessionData]]:
    packets = []
    while data:
        print(len(data))
        packet, data = _parse(data)
        packets.append(packet)
    return packets
