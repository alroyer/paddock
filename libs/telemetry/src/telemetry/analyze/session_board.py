"""Session leaderboard: final classification or last-known positions."""

from .index import Index
from .laps import _completed_laps, best_lap_ms


def _name(index: Index, ci: int) -> str | None:
    for packet in index.participants:
        if ci < len(packet.participants):
            return packet.participants[ci].name
    return None


def session_board(index: Index) -> list[dict]:
    """Board of all active cars, ordered by final position.

    Uses the final classification packet when present; otherwise falls
    back to the last completed lap position of each car.
    """
    board: list[dict] = []
    if index.final_classification is not None:
        fc = index.final_classification
        for ci, entry in enumerate(fc.classification_data):
            board.append(
                {
                    "position": entry.position,
                    "car_idx": ci,
                    "name": _name(index, ci) or f"car_{ci}",
                    "num_laps": entry.num_laps,
                    "best_lap_ms": entry.best_lap_time_in_ms or None,
                    "num_pit_stops": entry.num_pit_stops,
                    "result_status": entry.result_status,
                }
            )
        board.sort(key=lambda row: row["position"])
        return board

    for ci in range(index.n_cars):
        laps = _completed_laps(index, ci)
        if not laps:
            continue
        last = laps[-1]
        board.append(
            {
                "position": last["position"],
                "car_idx": ci,
                "name": _name(index, ci) or f"car_{ci}",
                "num_laps": len(laps),
                "best_lap_ms": best_lap_ms(index, ci),
                "num_pit_stops": laps[-1]["num_pit_stops"],
                "result_status": None,
            }
        )
    board.sort(key=lambda row: (row["position"] or 0))
    return board
