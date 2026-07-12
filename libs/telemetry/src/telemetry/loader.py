from pathlib import Path

from .packet import BasePacket, PacketEventData, PacketHeader


def load_telemetry(path: str | Path) -> list[BasePacket]:
    with open(path, "rb") as f:
        data = f.read()

    packets: list[BasePacket] = []

    while data:
        header = PacketHeader.from_bytes(data[: PacketHeader.SIZE])
        match header.packet_id:
            # case 0:
            #     from .packet.motion_ex import MotionExPacket

            #     packet = MotionExPacket.from_bytes(data)
            #     return [packet]
            # case 1:
            #     from .packet.session import SessionPacket

            #     packet = SessionPacket.from_bytes(data)
            #     return [packet]
            # case 2:
            #     from .packet.lap_data import LapDataPacket

            #     packet = LapDataPacket.from_bytes(data)
            #     return [packet]
            case 3:
                packet = PacketEventData.from_bytes(data)
                packets.append(packet)
                data = data[PacketEventData.SIZE :]
            # case 4:
            #     from .packet.participants import ParticipantsPacket

            #     packet = ParticipantsPacket.from_bytes(data)
            #     return [packet]
            # case 5:
            #     from .packet.car_setup import CarSetupPacket

            #     packet = CarSetupPacket.from_bytes(data)
            #     return [packet]
            # case 6:
            #     from .packet.car_telemetry import CarTelemetryPacket

            #     packet = CarTelemetryPacket.from_bytes(data)
            #     return [packet]
            # case 7:
            #     from .packet.car_status import CarStatusPacket

            #     packet = CarStatusPacket.from_bytes(data)
            #     return [packet]
            # case 8:
            #     from .packet.final_classification import FinalClassificationPacket

            #     packet = FinalClassificationPacket.from_bytes(data)
            #     return [packet]
            # case 9:
            #     from .packet.lobby_info import LobbyInfoPacket

            #     packet = LobbyInfoPacket.from_bytes(data)
            #     return [packet]
            case _:
                raise ValueError(f"Unknown packet_id: {header.packet_id}")

    return packets

    # packets: dict[str, list] = {
    #     "header": [header],
    #     "motion_ex": [],
    #     "car_telemetry": [],
    #     "car_status": [],
    #     "car_damage": [],
    #     "session": [],
    # }

    # offset = 102  # after header
    # while offset < len(data):
    #     packet_id = data[offset + 44]  # offset dans PacketHeader
    #     parser = PACKET_REGISTRY.get(packet_id)
    #     if parser:
    #         packet = parser.from_bytes(data[offset:])
    #         packets[parser.TYPE_NAME].append(packet)
    #     offset += packet.SIZE  # ou la taille réelle du packet

    # return packets
