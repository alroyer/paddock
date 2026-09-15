"""Fuel analysis: load, consumption and range from car status samples."""

from .index import Index
from .laps import lap_summaries


def _fuel_samples(index: Index, ci: int) -> list[tuple[float, float, float]]:
    """(session_time, fuel_in_tank, fuel_capacity) samples, time ordered."""
    return [
        (pkt.header.session_time, cs.fuel_in_tank, cs.fuel_capacity)
        for pkt in index.cars[ci].car_status
        for cs in [pkt.car_status_data[ci]]
    ]


def fuel_profile(index: Index, ci: int, max_points: int = 240) -> dict:
    """Downsampled fuel load over time + derived consumption stats.

    - ``points``: (t, fuel_kg) pairs, capped at ``max_points``
    - ``start_kg`` / ``end_kg``: first / last sample
    - ``capacity_kg``: nominal tank capacity
    - ``consumption_kg_per_lap``: total drop divided by laps elapsed
    """
    if max_points < 1:
        raise ValueError("max_points must be at least 1")
    samples = _fuel_samples(index, ci)
    if not samples:
        return {
            "points": [],
            "start_kg": None,
            "end_kg": None,
            "capacity_kg": None,
            "consumption_kg_per_lap": None,
        }

    if len(samples) > max_points:
        step = (len(samples) - 1) / (max_points - 1)
        picks = {round(i * step) for i in range(max_points)}
        samples = [s for i, s in enumerate(samples) if i in picks]

    points = [(t, fuel) for t, fuel, _ in samples]
    start_kg, end_kg = samples[0][1], samples[-1][1]
    capacity_kg = samples[0][2]
    drop = start_kg - end_kg

    consumption = None
    laps = lap_summaries(index, ci)
    if laps and drop > 0:
        consumption = round(drop / len(laps), 3)

    return {
        "points": points,
        "start_kg": round(start_kg, 2),
        "end_kg": round(end_kg, 2),
        "capacity_kg": round(capacity_kg, 2),
        "consumption_kg_per_lap": consumption,
    }
