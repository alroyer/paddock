from pathlib import Path

from .packet import PACKET_PARSERS, BasePacket, PacketHeader


def load_telemetry(path: str | Path) -> list[BasePacket]:
    with open(path, "rb") as f:
        data = f.read()
    packets: list[BasePacket] = []
    while data:
        header, data = PacketHeader.parse(data)
        packet, data = PACKET_PARSERS[header.packet_id](header, data)
        print(f"Loaded packet: {packet.__class__.__name__} (ID: {header.packet_id})")
        packets.append(packet)
    return packets
