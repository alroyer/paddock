from pathlib import Path

from .packet import BasePacket, PacketHeader
from .parsers import PACKET_PARSERS


def load_telemetry(path: str | Path) -> list[BasePacket]:
    """Load telemetry packets from file.

    Uses a memoryview over the file buffer to avoid allocating new bytes
    objects on every slice during parsing (significant performance gain).
    """
    with open(path, "rb") as f:
        buf = f.read()

    data = memoryview(buf)
    packets: list[BasePacket] = []
    while len(data) > 0:
        header, data = PacketHeader.parse(data)
        try:
            parser = PACKET_PARSERS[header.packet_id]
        except KeyError as exc:
            raise ValueError(f"unsupported packet_id: {header.packet_id}") from exc
        packet, data = parser(header, bytes(data))
        packets.append(packet)
    return packets
