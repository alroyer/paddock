from types import SimpleNamespace
from typing import cast

import pytest
from telemetry.analyze.driving import (
    _telemetry_samples,
    gear_usage,
    speed_trace,
)
from telemetry.analyze.index import Index


def telemetry_packet(time: float, speed: int, gear: int):
    return SimpleNamespace(
        header=SimpleNamespace(session_time=time),
        car_telemetry_data=[SimpleNamespace(speed=speed, gear=gear)],
    )


def index_with(packets=None):
    return cast(
        Index,
        SimpleNamespace(
            cars={0: SimpleNamespace(car_telemetry=packets or [])},
        ),
    )


def test_telemetry_samples_extracts_time_and_car_telemetry():
    packets = [telemetry_packet(1.5, 120, 4), telemetry_packet(2.5, 140, 5)]

    samples = _telemetry_samples(index_with(packets), 0)

    assert [(time, data.speed, data.gear) for time, data in samples] == [
        (1.5, 120, 4),
        (2.5, 140, 5),
    ]


def test_speed_trace_returns_all_samples_when_under_max_points():
    index = index_with(
        [
            telemetry_packet(1.0, 100, 3),
            telemetry_packet(2.0, 110, 4),
        ]
    )

    assert speed_trace(index, 0, max_points=3) == [
        (1.0, 100),
        (2.0, 110),
    ]


def test_speed_trace_downsamples_evenly_and_keeps_first_and_last_points():
    index = index_with([telemetry_packet(float(i), i * 10, 3) for i in range(10)])

    assert speed_trace(index, 0, max_points=4) == [
        (0.0, 0),
        (3.0, 30),
        (6.0, 60),
        (9.0, 90),
    ]


def test_speed_trace_returns_empty_for_missing_telemetry():
    assert speed_trace(index_with(), 0) == []


@pytest.mark.parametrize("max_points", [0, -1])
def test_speed_trace_rejects_nonpositive_max_points(max_points):
    with pytest.raises(ValueError, match="max_points must be at least 1"):
        speed_trace(index_with([telemetry_packet(1.0, 100, 3)]), 0, max_points)


def test_gear_usage_ignores_neutral_and_sorts_gears_with_shares():
    index = index_with(
        [
            telemetry_packet(1.0, 100, 0),
            telemetry_packet(2.0, 100, 4),
            telemetry_packet(3.0, 100, 2),
            telemetry_packet(4.0, 100, 4),
        ]
    )

    assert gear_usage(index, 0) == [
        {"gear": 2, "samples": 1, "share": 0.3333},
        {"gear": 4, "samples": 2, "share": 0.6667},
    ]


def test_gear_usage_returns_empty_when_all_samples_are_nonpositive_gears():
    index = index_with([telemetry_packet(1.0, 100, 0), telemetry_packet(2.0, 100, -1)])

    assert gear_usage(index, 0) == []
