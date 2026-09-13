from dataclasses import dataclass
from functools import singledispatch


@dataclass(frozen=True)
class RecorderEvent:
    message: str


@dataclass(frozen=True)
class RecorderStartedEvent(RecorderEvent):
    pass


@dataclass(frozen=True)
class RecorderStoppedEvent(RecorderEvent):
    pass


@singledispatch
def handle_event(event: RecorderEvent) -> None:
    pass
