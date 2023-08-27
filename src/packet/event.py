from dataclasses import dataclass
from typing import Union

from .constants import BUTTON_FLAGS
from .information import PacketHeader


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


@dataclass
class Overtake:
    overtaking_vehicle_idx: int
    being_overtaken_vehicle_idx: int


@dataclass
class PacketEventData:
    header: PacketHeader
    event_string_code: str
    event_details: Union[
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


def button_status_to_buttons(button_status: int) -> list[str]:
    buttons = []
    for bit_flag, button in BUTTON_FLAGS.items():
        if bit_flag & button_status:
            buttons.append(button)
    return buttons
