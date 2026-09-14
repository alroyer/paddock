"""Resolve human car references (driver name) to ``car_idx``."""

from .index import Index
from .types import UnknownCar


def resolve_car(index: Index, ref: int | str) -> int:
    """Return the ``car_idx`` for a car reference.

    Accepts a ``car_idx`` (int) or a driver name (str, matched
    case-insensitively against ``PacketParticipantsData``).
    """
    if isinstance(ref, int):
        car = index.cars.get(ref)
        if car is None or not _car_active(index, ref):
            raise UnknownCar(f"no telemetry for car_idx {ref}")
        return ref

    name = ref.strip().casefold()
    if not name:
        raise UnknownCar("empty car name")

    for packet in index.participants:
        for ci, participant in enumerate(packet.participants):
            if participant.name.casefold() == name:
                return ci

    raise UnknownCar(f"unknown driver '{ref}' (known: {_known_names(index)})")


def _car_active(index: Index, car_idx: int) -> bool:
    return car_idx < index.n_cars


def _known_names(index: Index) -> str:
    if not index.participants:
        return "none"
    return ", ".join(p.name for p in index.participants[0].participants[: index.n_cars])
