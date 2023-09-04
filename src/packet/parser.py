import logging
import struct
from typing import Tuple, Union

from .event import Buttons, PacketEventData, SessionEnded, SessionStarted
from .header import PacketHeader
from .lapdata import PacketLapData
from .motion import PacketMotionData
from .participant import PacketParticipantsData
from .session import PacketSessionData

logger = logging.getLogger(__name__)


def _read(data: bytes, count: int) -> Tuple[bytes, bytes]:
    return data[:count], data[count:]


def _parse(data: bytes) -> Tuple[Union[PacketEventData, PacketLapData, PacketMotionData, PacketSessionData], bytes]:
    bytes_count = PacketHeader.bytes_count()
    packet_header = PacketHeader(*struct.unpack(PacketHeader.unpack_format(), data[:bytes_count]))
    packet_handler = PACKET_DATA_HANDLER[packet_header.packet_id]
    return packet_handler(packet_header, data[bytes_count:])


def _parse_event_data(packet_header: PacketHeader, data: bytes) -> Tuple[PacketEventData, bytes]:
    bytes_count = PacketEventData.bytes_count()
    event_string_bytes_count = PacketEventData.event_string_code_bytes_count()
    event_data, remaining_data = _read(data, bytes_count)
    event_string_code = ''.join(
        [
            chr(b)
            for b in struct.unpack(
                PacketEventData.event_string_code_unpack_format(), event_data[:event_string_bytes_count]
            )
        ]
    )
    event_handler = EVENT_HANDLER[event_string_code]
    return event_handler(packet_header, event_string_code, event_data[event_string_bytes_count:]), remaining_data


def _parse_session_data(packet_header: PacketHeader, data: bytes) -> Tuple[PacketSessionData, bytes]:
    bytes_count = PacketSessionData.bytes_count()
    session_data, remaining_data = _read(data, bytes_count)
    # TODO
    packet_session_data = PacketSessionData(
        packet_header, *struct.unpack(PacketSessionData.unpack_format(), session_data[:4])
    )
    return packet_session_data, remaining_data


def _parse_participants_data(packet_header: PacketHeader, data: bytes) -> Tuple[PacketParticipantsData, bytes]:
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


PACKET_DATA_HANDLER = {
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
        packet, data = _parse(data)
        packets.append(packet)
        logger.info(packet)
    return packets
