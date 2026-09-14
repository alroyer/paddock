"""Lap-level analysis: completed laps, sectors, comparisons."""

from .index import Index
from .types import UnknownLap


def _completed_laps(index: Index, ci: int) -> list[dict]:
    """One entry per completed lap, oldest first.

    A lap is considered completed when ``current_lap_num`` advances past it;
    the last sample for a given completed lap wins (dedup of periodic P2).
    """
    by_lap: dict[int, dict] = {}
    for pkt in index.cars[ci].lap_data:
        ld = pkt.lap_data[ci]
        lap_num = ld.current_lap_num - 1
        if lap_num < 1:
            continue
        by_lap[lap_num] = {
            "lap": lap_num,
            "t_session": pkt.header.session_time,
            "lap_time_ms": ld.last_lap_time_in_ms,
            "sectors_ms": [
                _sector_ms(ld.sector1_time_ms_part, ld.sector1_time_minutes_part),
                _sector_ms(ld.sector2_time_ms_part, ld.sector2_time_minutes_part),
            ],
            "position": ld.car_position,
            "grid_position": ld.grid_position,
            "pit_status": ld.pit_status,
            "num_pit_stops": ld.num_pit_stops,
            "invalidated": bool(ld.current_lap_invalid),
            "delta_to_car_in_front_ms": _delta_ms(
                ld.delta_to_car_in_front_ms_part, ld.delta_to_car_in_front_minutes_part
            ),
            "delta_to_leader_ms": _delta_ms(
                ld.delta_to_race_leader_ms_part, ld.delta_to_race_leader_minutes_part
            ),
        }
    return [by_lap[k] for k in sorted(by_lap)]


def _delta_ms(ms_part: int, minutes_part: int) -> int:
    return ms_part + minutes_part * 60_000


def _sector_ms(ms_part: int, minutes_part: int) -> int:
    return ms_part + minutes_part * 60_000


def lap_summaries(index: Index, ci: int) -> list[dict]:
    """All completed laps of a car, oldest first."""
    return _completed_laps(index, ci)


def lap_summary(index: Index, ci: int, lap: int) -> dict:
    """One completed lap. Raises UnknownLap if not found."""
    for entry in _completed_laps(index, ci):
        if entry["lap"] == lap:
            return entry
    raise UnknownLap(f"car {ci} has no completed lap {lap}")


def sector_breakdown(index: Index, ci: int, lap: int) -> dict:
    """Sectors of one lap + best sector of the session per sector index."""
    entry = lap_summary(index, ci, lap)
    sectors = entry["sectors_ms"] or []
    best = _best_sectors(index, ci)
    return {
        "lap": lap,
        "sectors_ms": sectors,
        "best_sector_ms": [
            sectors[i] if i < len(sectors) else None for i in range(len(sectors))
        ],
        "session_best_ms": best,
    }


def _best_sectors(index: Index, ci: int) -> list[int | None]:
    best: list[int | None] = [None, None]
    for pkt in index.cars[ci].lap_data:
        ld = pkt.lap_data[ci]
        sectors = [
            _sector_ms(ld.sector1_time_ms_part, ld.sector1_time_minutes_part),
            _sector_ms(ld.sector2_time_ms_part, ld.sector2_time_minutes_part),
        ]
        for i, s in enumerate(sectors):
            if s and (best[i] is None or s < best[i]):
                best[i] = s
    return best


def compare_laps(index: Index, ci: int, lap_a: int, lap_b: int) -> dict:
    """Lap A vs lap B: time and per-sector differences (a - b, in ms)."""
    a = lap_summary(index, ci, lap_a)
    b = lap_summary(index, ci, lap_b)
    sa = a["sectors_ms"] or []
    sb = b["sectors_ms"] or []
    n = max(len(sa), len(sb))
    diffs = [
        (sa[i] - sb[i]) if (i < len(sa) and i < len(sb) and sa[i] and sb[i]) else None
        for i in range(n)
    ]
    return {
        "car_idx": ci,
        "lap_a": a,
        "lap_b": b,
        "delta_ms": a["lap_time_ms"] - b["lap_time_ms"],
        "sector_diffs_ms": diffs,
    }


def best_laps(index: Index, ci: int, limit: int = 3) -> list[dict]:
    """Fastest valid laps of a car, best first."""
    laps = [
        lap
        for lap in _completed_laps(index, ci)
        if not lap["invalidated"] and lap["lap_time_ms"]
    ]
    laps.sort(key=lambda lap: lap["lap_time_ms"])
    return laps[:limit]


def best_lap_ms(index: Index, ci: int) -> int | None:
    laps = best_laps(index, ci, limit=1)
    return laps[0]["lap_time_ms"] if laps else None
