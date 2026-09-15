from collections.abc import Iterable

from .packet import BasePacket, PacketId


def list_sessions(packets: Iterable[BasePacket]) -> list[int]:
    sessions: set[int] = set()
    for packet in packets:
        sessions.add(packet.header.session_uid)
    return sorted(sessions)


def filter_packets(
    packets: Iterable[BasePacket],
    *,
    packet_id: PacketId | None = None,
    session: int | None = None,
) -> list[BasePacket]:
    filtered_packets = packets
    if packet_id is not None:
        filtered_packets = [
            packet
            for packet in filtered_packets
            if packet.header.packet_id == packet_id
        ]
    if session is not None:
        filtered_packets = [
            packet
            for packet in filtered_packets
            if packet.header.session_uid == session
        ]
    return list(filtered_packets)
