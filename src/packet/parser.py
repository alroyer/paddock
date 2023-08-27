from typing import Union

from .event import PacketEventData
from .information import PacketHeader
from .lapdata import PacketLapData
from .motion import PacketMotionData
from .session import PacketSessionData


def parse(data: bytes) -> Union[PacketEventData, PacketLapData, PacketMotionData, PacketSessionData]:
    # TODO
    pass
