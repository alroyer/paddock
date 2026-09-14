"""Tyre analysis: stints, wear and degradation per compound."""

from bisect import bisect_right

from .index import Index
from .laps import _completed_laps
from .naming import tyre_compound_name


def _status_samples(index: Index, ci: int) -> list[tuple[float, int, int]]:
    """(session_time, compound, tyres_age_laps) samples, time ordered."""
    return [
        (pkt.header.session_time, cs.actual_tyre_compound, cs.tyres_age_laps)
        for pkt in index.cars[ci].car_status
        for cs in [pkt.car_status_data[ci]]
    ]


def _status_at(index: Index, ci: int, t: float) -> tuple[int, int] | None:
    """Compound and tyre age at time t (latest sample at or before t)."""
    samples = _status_samples(index, ci)
    if not samples:
        return None
    times = [s[0] for s in samples]
    i = bisect_right(times, t) - 1
    if i < 0:
        return None
    return samples[i][1], samples[i][2]


def tyre_strategy(index: Index, ci: int) -> list[dict]:
    """Tyre stints of a car, ordered.

    A new stint starts when the compound changes or the tyre age resets
    (new set fitted at the pit wall).
    """
    stints: list[dict] = []
    for t, compound, age in _status_samples(index, ci):
        last = stints[-1] if stints else None
        if last is None or compound != last["compound"] or age < last["end_age_laps"]:
            stints.append(
                {
                    "compound": compound,
                    "compound_name": tyre_compound_name(compound),
                    "start_t": t,
                    "end_t": t,
                    "start_age_laps": age,
                    "end_age_laps": age,
                }
            )
        else:
            last["end_t"] = t
            last["end_age_laps"] = max(last["end_age_laps"], age)
    for stint in stints:
        stint["laps"] = max(stint["end_age_laps"] - stint["start_age_laps"], 0)
    return stints


def tyre_degradation(index: Index, ci: int) -> dict:
    """Lap time vs tyre age, grouped by compound.

    Returns {compound_id: [{lap, lap_time_ms, tyres_age_laps}, ...]} sorted
    by age; useful to spot the wear curve per compound.
    """
    out: dict[int, list[dict]] = {}
    for lap in _completed_laps(index, ci):
        status = _status_at(index, ci, lap["t_session"])
        if status is None or not lap["lap_time_ms"]:
            continue
        compound, age = status
        out.setdefault(compound, []).append(
            {
                "lap": lap["lap"],
                "lap_time_ms": lap["lap_time_ms"],
                "tyres_age_laps": age,
            }
        )
    for rows in out.values():
        rows.sort(key=lambda row: row["tyres_age_laps"])
    return out
