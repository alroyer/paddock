from types import SimpleNamespace
from typing import cast

from telemetry.analyze import fuel as fuel_mod
from telemetry.analyze.fuel import _fuel_samples, fuel_profile
from telemetry.analyze.index import Index


def status_packet(time: float, fuel: float, capacity: float):
    return SimpleNamespace(
        header=SimpleNamespace(session_time=time),
        car_status_data=[SimpleNamespace(fuel_in_tank=fuel, fuel_capacity=capacity)],
    )


def index_with(status=None):
    return cast(
        Index,
        SimpleNamespace(
            cars={0: SimpleNamespace(car_status=status or [])},
        ),
    )


def test_fuel_samples_extracts_time_fuel_and_capacity():
    packets = [status_packet(1.0, 42.5, 110.0)]

    assert _fuel_samples(index_with(packets), 0) == [(1.0, 42.5, 110.0)]


def test_fuel_profile_returns_empty_values_without_status_samples():
    assert fuel_profile(index_with(), 0) == {
        "points": [],
        "start_kg": None,
        "end_kg": None,
        "capacity_kg": None,
        "consumption_kg_per_lap": None,
    }


def test_fuel_profile_rounds_values_and_calculates_consumption_per_lap(
    monkeypatch,
):
    index = index_with(
        [
            status_packet(1.0, 10.123, 110.555),
            status_packet(2.0, 8.5, 110.0),
            status_packet(3.0, 7.0, 109.0),
        ]
    )
    monkeypatch.setattr(fuel_mod, "lap_summaries", lambda index, ci: [{}, {}, {}])

    assert fuel_profile(index, 0) == {
        "points": [(1.0, 10.123), (2.0, 8.5), (3.0, 7.0)],
        "start_kg": 10.12,
        "end_kg": 7.0,
        "capacity_kg": 110.56,
        "consumption_kg_per_lap": 1.041,
    }


def test_fuel_profile_downsamples_points_and_keeps_first_and_last(monkeypatch):
    index = index_with([status_packet(float(i), 100.0 - i, 110.0) for i in range(10)])
    monkeypatch.setattr(fuel_mod, "lap_summaries", lambda index, ci: [])

    assert fuel_profile(index, 0, max_points=4)["points"] == [
        (0.0, 100.0),
        (3.0, 97.0),
        (6.0, 94.0),
        (9.0, 91.0),
    ]


def test_fuel_profile_has_no_consumption_without_laps_or_positive_drop(
    monkeypatch,
):
    monkeypatch.setattr(fuel_mod, "lap_summaries", lambda index, ci: [{"lap": 1}])
    assert (
        fuel_profile(
            index_with(
                [status_packet(1.0, 8.0, 100.0), status_packet(2.0, 8.0, 100.0)]
            ),
            0,
        )["consumption_kg_per_lap"]
        is None
    )

    monkeypatch.setattr(fuel_mod, "lap_summaries", lambda index, ci: [])
    assert (
        fuel_profile(
            index_with(
                [status_packet(1.0, 8.0, 100.0), status_packet(2.0, 6.0, 100.0)]
            ),
            0,
        )["consumption_kg_per_lap"]
        is None
    )
