from typing import Iterable

from .packet import BasePacket


def list_sessions(packets: Iterable[BasePacket]) -> list[str]:
    sessions = set()
    for packet in packets:
        # TODO: This is a hack to get the session_uid from the packet. We should probably have a better way to do this.
        header = getattr(packet, "header")
        sessions.add(header.session_uid)
    return list(sessions)


def list_packets(session: str, packets: Iterable[BasePacket]) -> list[BasePacket]:
    return [
        packet for packet in packets if getattr(packet, "header").session_uid == session
    ]
