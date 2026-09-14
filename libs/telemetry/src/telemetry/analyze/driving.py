"""Driving analysis: speed traces and gear usage from car telemetry."""

from .index import Index


def _telemetry_samples(index: Index, ci: int) -> list:
    """(session_time, CarTelemetryData) for one car, time ordered."""
    return [
        (pkt.header.session_time, ct)
        for pkt in index.cars[ci].car_telemetry
        for ct in [pkt.car_telemetry_data[ci]]
    ]


def speed_trace(index: Index, ci: int, max_points: int = 240) -> list:
    """Downsampled (t, speed_kmh) points for the whole session."""
    samples = _telemetry_samples(index, ci)
    if not samples:
        return []
    if len(samples) > max_points:
        step = (len(samples) - 1) / (max_points - 1)
        picks = {round(i * step) for i in range(max_points)}
        samples = [s for i, s in enumerate(samples) if i in picks]
    return [(t, ct.speed) for t, ct in samples]


def gear_usage(index: Index, ci: int) -> list:
    """Gear usage histogram: [{gear, samples}, ...] sorted by gear."""
    samples = _telemetry_samples(index, ci)
    counts: dict[int, int] = {}
    for _, ct in samples:
        if ct.gear > 0:
            counts[ct.gear] = counts.get(ct.gear, 0) + 1
    total = sum(counts.values()) or 1
    return [
        {"gear": gear, "samples": count, "share": round(count / total, 4)}
        for gear, count in sorted(counts.items())
    ]
