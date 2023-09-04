from dataclasses import dataclass
from typing import Union

from .header import PacketHeader


@dataclass
class FastestLap:
    # TODO
    pass


@dataclass
class Retirement:
    # TODO
    pass


@dataclass
class TeamMateInPits:
    # TODO
    pass


@dataclass
class RaceWinner:
    # TODO
    pass


@dataclass
class Penalty:
    # TODO
    pass


@dataclass
class SpeedTrap:
    # TODO
    pass


@dataclass
class StartLight:
    num_lights: int


@dataclass
class DriveThroughPenaltyServed:
    vehicle_idx: int


@dataclass
class StopGoPenaltyServed:
    vehicle_idx: int


@dataclass
class Flashback:
    # TODO
    pass


@dataclass
class Buttons:
    button_status: int

    def __str__(self) -> str:
        buttons = _button_status_to_buttons(self.button_status)
        return f'''[Buttons]
    buttons:           {buttons}'''


@dataclass
class Overtake:
    overtaking_vehicle_idx: int
    being_overtaken_vehicle_idx: int


@dataclass
class SessionStarted:
    def __str__(self) -> str:
        return '''[SessionStarted]'''


@dataclass
class SessionEnded:
    def __str__(self) -> str:
        return '''[SessionEnded]'''


@dataclass
class PacketEventData:
    header: PacketHeader
    event_string_code: str
    event_details: Union[
        SessionStarted,
        SessionEnded,
        FastestLap,
        Retirement,
        TeamMateInPits,
        RaceWinner,
        Penalty,
        SpeedTrap,
        StartLight,
        DriveThroughPenaltyServed,
        StopGoPenaltyServed,
        Flashback,
        Buttons,
        Overtake,
    ]

    @classmethod
    def bytes_count(cls) -> int:
        return 45 - PacketHeader.bytes_count()

    @classmethod
    def event_string_code_bytes_count(cls) -> int:
        return 4

    @classmethod
    def event_string_code_unpack_format(cls) -> str:
        return '<BBBB'

    def __str__(self) -> str:
        return f'''[PacketEventData]
    {self.header}
    event:             {_event_string_code_to_str(self.event_string_code)}
    {self.event_details}'''


BUTTON_FLAGS = {
    0x00000001: 'Cross or A',
    0x00000002: 'Triangle or Y',
    0x00000004: 'Circle or B',
    0x00000008: 'Square or X',
    0x00000010: 'D-pad Left',
    0x00000020: 'D-pad Right',
    0x00000040: 'D-pad Up',
    0x00000080: 'D-pad Down',
    0x00000100: 'Options or Menu',
    0x00000200: 'L1 or LB',
    0x00000400: 'R1 or RB',
    0x00000800: 'L2 or LT',
    0x00001000: 'R2 or RT',
    0x00002000: 'Left Stick Click',
    0x00004000: 'Right Stick Click',
    0x00008000: 'Right Stick Left',
    0x00010000: 'Right Stick Right',
    0x00020000: 'Right Stick Up',
    0x00040000: 'Right Stick Down',
    0x00080000: 'Special',
    0x00100000: 'UDP Action 1',
    0x00200000: 'UDP Action 2',
    0x00400000: 'UDP Action 3',
    0x00800000: 'UDP Action 4',
    0x01000000: 'UDP Action 5',
    0x02000000: 'UDP Action 6',
    0x04000000: 'UDP Action 7',
    0x08000000: 'UDP Action 8',
    0x10000000: 'UDP Action 9',
    0x20000000: 'UDP Action 10',
    0x40000000: 'UDP Action 11',
    0x80000000: 'UDP Action 12',
}


def _button_status_to_buttons(button_status: int) -> list[str]:
    buttons = []
    for bit_flag, button in BUTTON_FLAGS.items():
        if bit_flag & button_status:
            buttons.append(button)
    return buttons


EVENT_STRING_CODE_DEFINITION = {
    'SSTA': 'Session Started',
    'SEND': 'Session Ended',
    'FTLP': 'Fastest Lap',
    'RTMT': 'Retirement',
    'DRSE': 'DRS enabled',
    'DRSD': 'DRS disabled',
    'TMPT': 'Team mate in pits',
    'CHQF': 'Chequered flag',
    'RCWN': 'Race Winner',
    'PENA': 'Penalty Issued',
    'SPTP': 'Speed Trap Triggered',
    'STLG': 'Start lights',
    'LGOT': 'Lights out',
    'DTSV': 'Drive through served',
    'SGSV': 'Stop go served',
    'FLBK': 'Flashback',
    'BUTN': 'Button status',
    'RDFL': 'Red Flag',
    'OVTK': 'Overtake',
}


def _event_string_code_to_str(event_string_code: str) -> str:
    return EVENT_STRING_CODE_DEFINITION[event_string_code]
