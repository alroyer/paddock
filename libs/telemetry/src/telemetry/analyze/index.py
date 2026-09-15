"""In-memory index of parsed packets, grouped per car.

The index is built once (``build_index``) so that every analysis runs in
O(car x laps) instead of O(file).
"""

from dataclasses import dataclass, field

from ..packet import (
    BasePacket,
    PacketCarStatusData,
    PacketCarTelemetryData,
    PacketEventData,
    PacketFinalClassificationData,
    PacketLapData,
    PacketMotionData,
    PacketParticipantsData,
    PacketSessionData,
    PacketTyreSetsData,
)


@dataclass
class CarIndex:
    """Time-ordered high-frequency packets for a single car (car_idx)."""

    motion: list[PacketMotionData] = field(default_factory=list)
    car_telemetry: list[PacketCarTelemetryData] = field(default_factory=list)
    car_status: list[PacketCarStatusData] = field(default_factory=list)
    lap_data: list[PacketLapData] = field(default_factory=list)
    tyre_sets: list[PacketTyreSetsData] = field(default_factory=list)


@dataclass
class Index:
    cars: dict[int, CarIndex]
    participants: list[PacketParticipantsData]
    session: PacketSessionData | None
    final_classification: PacketFinalClassificationData | None
    events: list[PacketEventData]
    n_cars: int
    session_uid: int
    game_year: int
    player_car_index: int
    t_min: float
    t_max: float
    packet_counts: dict[int, int]


def build_index(packets: list[BasePacket]) -> Index:
    """Group parsed packets per car, in session-time order."""
    if not packets:
        raise ValueError("no packets to index")

    cars: dict[int, CarIndex] = {}
    events: list[PacketEventData] = []
    participants: list[PacketParticipantsData] = []
    session: PacketSessionData | None = None
    final_classification: PacketFinalClassificationData | None = None
    packet_counts: dict[int, int] = {}

    def car(ci: int) -> CarIndex:
        idx = cars.get(ci)
        if idx is None:
            idx = cars[ci] = CarIndex()
        return idx

    for packet in packets:
        pid = int(packet.header.packet_id)
        packet_counts[pid] = packet_counts.get(pid, 0) + 1

        if isinstance(packet, PacketMotionData):
            for ci, _ in enumerate(packet.car_motion_data):
                car(ci).motion.append(packet)
        elif isinstance(packet, PacketCarTelemetryData):
            for ci, _ in enumerate(packet.car_telemetry_data):
                car(ci).car_telemetry.append(packet)
        elif isinstance(packet, PacketCarStatusData):
            for ci, _ in enumerate(packet.car_status_data):
                car(ci).car_status.append(packet)
        elif isinstance(packet, PacketLapData):
            for ci, _ in enumerate(packet.lap_data):
                car(ci).lap_data.append(packet)
        elif isinstance(packet, PacketTyreSetsData):
            car(packet.car_idx).tyre_sets.append(packet)
        elif isinstance(packet, PacketEventData):
            events.append(packet)
        elif isinstance(packet, PacketParticipantsData):
            participants.append(packet)
        elif isinstance(packet, PacketSessionData) and session is None:
            session = packet
        elif (
            isinstance(packet, PacketFinalClassificationData)
            and final_classification is None
        ):
            final_classification = packet

    for car_index in cars.values():
        for packet_list in (
            car_index.motion,
            car_index.car_telemetry,
            car_index.car_status,
            car_index.lap_data,
            car_index.tyre_sets,
        ):
            packet_list.sort(key=lambda packet: packet.header.session_time)
    events.sort(key=lambda packet: packet.header.session_time)
    participants.sort(key=lambda packet: packet.header.session_time)

    first = packets[0]
    t_times = [p.header.session_time for p in packets]
    n_cars = max(len(cars), 1)
    if participants:
        n_cars = participants[0].num_active_cars

    return Index(
        cars=cars,
        participants=participants,
        session=session,
        final_classification=final_classification,
        events=events,
        n_cars=n_cars,
        session_uid=first.header.session_uid,
        game_year=first.header.game_year,
        player_car_index=first.header.player_car_index,
        t_min=min(t_times),
        t_max=max(t_times),
        packet_counts=packet_counts,
    )
