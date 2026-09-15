from types import SimpleNamespace
from typing import cast

import pytest
from telemetry.analyze import laps as laps_mod
from telemetry.analyze.index import Index
from telemetry.analyze.types import UnknownLap


def lap_packet(
    time: float,
    current_lap: int,
    lap_time: int,
    sector1: int,
    sector2: int,
    *,
    sector1_minutes: int = 0,
    sector2_minutes: int = 0,
    invalidated: int = 0,
):
    lap = SimpleNamespace(
        current_lap_num=current_lap,
        last_lap_time_in_ms=lap_time,
        sector1_time_ms_part=sector1,
        sector1_time_minutes_part=sector1_minutes,
        sector2_time_ms_part=sector2,
        sector2_time_minutes_part=sector2_minutes,
        car_position=3,
        grid_position=5,
        pit_status=0,
        num_pit_stops=1,
        current_lap_invalid=invalidated,
        delta_to_car_in_front_ms_part=120,
        delta_to_car_in_front_minutes_part=1,
        delta_to_race_leader_ms_part=240,
        delta_to_race_leader_minutes_part=2,
    )
    return SimpleNamespace(header=SimpleNamespace(session_time=time), lap_data=[lap])


def index_with(packets=None):
    return cast(
        Index,
        SimpleNamespace(cars={0: SimpleNamespace(lap_data=packets or [])}),
    )


def test_time_ms_combines_minutes_and_milliseconds():
    assert laps_mod._time_ms(1234, 2) == 121234


def test_completed_laps_skips_in_progress_laps_deduplicates_and_sorts():
    duplicate = lap_packet(3.0, 2, 90100, 1100, 2200)
    index = index_with(
        [
            lap_packet(1.0, 1, 0, 0, 0),
            lap_packet(2.0, 3, 92000, 1000, 2000, sector1_minutes=1),
            duplicate,
            lap_packet(4.0, 2, 90000, 900, 1900),
        ]
    )

    result = laps_mod._completed_laps(index, 0)

    assert [lap["lap"] for lap in result] == [1, 2]
    assert result[0]["t_session"] == 4.0
    assert result[0]["lap_time_ms"] == 90000
    assert result[0]["sectors_ms"] == [900, 1900]
    assert result[0]["position"] == 3
    assert result[0]["invalidated"] is False
    assert result[0]["delta_to_car_in_front_ms"] == 60120
    assert result[0]["delta_to_leader_ms"] == 120240
    assert result[1]["sectors_ms"] == [61000, 2000]


def test_lap_summaries_returns_completed_laps():
    index = index_with([lap_packet(1.0, 2, 90000, 1000, 2000)])

    assert laps_mod.lap_summaries(index, 0) == laps_mod._completed_laps(index, 0)


def test_lap_summary_returns_requested_lap_or_raises_unknown_lap():
    index = index_with([lap_packet(1.0, 2, 90000, 1000, 2000)])

    assert laps_mod.lap_summary(index, 0, 1)["lap_time_ms"] == 90000
    with pytest.raises(UnknownLap, match="car 0 has no completed lap 2"):
        laps_mod.lap_summary(index, 0, 2)


def test_sector_breakdown_reports_lap_sectors_and_session_bests():
    index = index_with(
        [
            lap_packet(1.0, 2, 90000, 1000, 2000),
            lap_packet(2.0, 3, 91000, 900, 2200),
        ]
    )

    assert laps_mod.sector_breakdown(index, 0, 1) == {
        "lap": 1,
        "sectors_ms": [1000, 2000],
        "best_sector_ms": [900, 2000],
        "session_best_ms": [900, 2000],
    }


def test_compare_laps_calculates_deltas_and_marks_missing_sector_values(
    monkeypatch,
):
    values = {
        1: {"lap": 1, "lap_time_ms": 91000, "sectors_ms": [100, 0]},
        2: {"lap": 2, "lap_time_ms": 90000, "sectors_ms": [80, 50]},
    }
    monkeypatch.setattr(
        laps_mod, "_completed_laps", lambda index, ci: list(values.values())
    )

    assert laps_mod.compare_laps(index_with(), 0, 1, 2) == {
        "car_idx": 0,
        "lap_a": values[1],
        "lap_b": values[2],
        "delta_ms": 1000,
        "sector_diffs_ms": [20, None],
    }


def test_best_laps_filters_invalid_and_missing_times_sorts_and_limits(
    monkeypatch,
):
    laps = [
        {"lap": 1, "lap_time_ms": 95000, "invalidated": False},
        {"lap": 2, "lap_time_ms": 0, "invalidated": False},
        {"lap": 3, "lap_time_ms": 90000, "invalidated": True},
        {"lap": 4, "lap_time_ms": 91000, "invalidated": False},
    ]
    monkeypatch.setattr(laps_mod, "_completed_laps", lambda index, ci: laps)

    assert laps_mod.best_laps(index_with(), 0, limit=1) == [laps[3]]


def test_best_lap_ms_returns_fastest_time_or_none(monkeypatch):
    monkeypatch.setattr(
        laps_mod,
        "best_laps",
        lambda index, ci, limit: [{"lap_time_ms": 87654}][:limit],
    )
    assert laps_mod.best_lap_ms(index_with(), 0) == 87654

    monkeypatch.setattr(laps_mod, "best_laps", lambda index, ci, limit: [])
    assert laps_mod.best_lap_ms(index_with(), 0) is None
