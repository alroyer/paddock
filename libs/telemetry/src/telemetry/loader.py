from pathlib import Path

from .packet import BasePacket, PacketEventData, PacketHeader, PacketMotionData


def load_telemetry(path: str | Path) -> list[BasePacket]:
    with open(path, "rb") as f:
        data = f.read()

    packets: list[BasePacket] = []

    while data:
        header, data = PacketHeader.parse(data)
        match header.packet_id:
            case 0:
                packet, data = PacketMotionData.parse(header, data)
                packets.append(packet)
            case 3:
                packet, data = PacketEventData.parse(header, data)
                packets.append(packet)
            case _:
                raise ValueError(f"Unknown packet_id: {header.packet_id}")

    return packets
