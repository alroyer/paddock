from dataclasses import dataclass


@dataclass
class PacketHeader:
    packet_format: int
    game_year: int
    game_major_version: int
    game_minor_version: int
    packet_version: int
    packet_id: int
    session_uid: int
    session_time: float
    frame_identifier: int
    overall_frame_identifier: int
    player_car_index: int
    secondary_player_car_index: int
    secondary_player_car_index: int

    @classmethod
    def bytes_count(cls) -> int:
        return 29

    @classmethod
    def unpack_format(cls) -> str:
        return '<HBBBBBQfIIBB'

    def __str__(self) -> str:
        # TODO
        return f'''[PacketHeader]
    packet format:     {self.packet_format}
    game year:         {self.game_year}
    version:           {self.game_major_version}.{self.game_minor_version}
    packet version:    {self.packet_version}
    packet id:         {_packet_id_to_str(self.packet_id)}
    session uid:       {self.session_uid}'''


PACKET_ID_DEFINITION = {
    0: 'Motion',
    1: 'Session',
    2: 'Lap',
    3: 'Event',
    4: 'Participants',
    5: 'Car Setups',
    6: 'Car Telemetry',
    7: 'Car Status',
    8: 'Final Classification',
    9: 'Lobby Info',
    10: 'Car Damage',
    11: 'Session History',
    12: 'Tyre Sets',
    13: 'Motion Ex',
}


def _packet_id_to_str(packet_id: int) -> str:
    return PACKET_ID_DEFINITION[packet_id]
