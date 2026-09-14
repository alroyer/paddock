"""Race strategy: pit stops and position changes."""

from .index import Index
from .laps import _completed_laps
from .naming import pit_status_name


def pit_stops(index: Index, ci: int) -> list[dict]:
    """Pit stops of a car, in lap order.

    A stop is detected when ``num_pit_stops`` increases between two laps.
    """
    stops: list[dict] = []
    prev = 0
    for lap in _completed_laps(index, ci):
        if lap["num_pit_stops"] > prev:
            stops.append(
                {
                    "lap": lap["lap"],
                    "t_session": lap["t_session"],
                    "pit_stop_number": prev + 1,
                    "pit_status": lap["pit_status"],
                    "pit_status_name": pit_status_name(lap["pit_status"]),
                    "lap_time_ms": lap["lap_time_ms"],
                }
            )
        prev = lap["num_pit_stops"]
    return stops


def position_changes(index: Index, ci: int) -> list[dict]:
    """Laps where the car changed position, with the delta.

    Positive ``delta`` = gained positions, negative = lost.
    """
    changes: list[dict] = []
    prev_pos: int | None = None
    for lap in _completed_laps(index, ci):
        pos = lap["position"]
        if prev_pos is not None and pos != prev_pos and pos > 0:
            changes.append(
                {
                    "lap": lap["lap"],
                    "t_session": lap["t_session"],
                    "from": prev_pos,
                    "to": pos,
                    "delta": pos - prev_pos,
                }
            )
        if pos > 0:
            prev_pos = pos
    return changes
