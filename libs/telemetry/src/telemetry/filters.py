from typing import Iterable

from .packet import BasePacket


def list_sessions(packets: Iterable[BasePacket]) -> list[str]:
    sessions = set()
    for packet in packets:
        # TODO: This is a hack to get the session_uid from the packet. We should probably have a better way to do this.
        header = getattr(packet, "header")
        sessions.add(header.session_uid)
    return list(sessions)


def filter_packets(
    packets: Iterable[BasePacket],
    session: str | None = None,
    packet_id: int | None = None,
) -> list[BasePacket]:
    filtered_packets = packets
    if session is not None:
        filtered_packets = [
            packet
            for packet in filtered_packets
            if getattr(packet, "header").session_uid == session
        ]
    if packet_id is not None:
        filtered_packets = [
            packet
            for packet in filtered_packets
            if getattr(packet, "header").packet_id == packet_id
        ]
    return list(filtered_packets)
