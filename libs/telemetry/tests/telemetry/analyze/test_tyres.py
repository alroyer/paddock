from types import SimpleNamespace
from typing import cast

from telemetry.analyze.index import Index
from telemetry.analyze.tyres import (
    _status_at,
    _status_samples,
    tyre_degradation,
    tyre_strategy,
)


def status_packet(time: float, compound: int, age: int):
    return SimpleNamespace(
        header=SimpleNamespace(session_time=time),
        car_status_data=[
            SimpleNamespace(actual_tyre_compound=compound, tyres_age_laps=age)
        ],
    )


def lap_packet(time: float, current_lap: int, lap_time: int):
    lap_data = SimpleNamespace(
        current_lap_num=current_lap,
        last_lap_time_in_ms=lap_time,
        sector1_time_ms_part=0,
        sector1_time_minutes_part=0,
        sector2_time_ms_part=0,
        sector2_time_minutes_part=0,
        car_position=1,
        grid_position=1,
        pit_status=0,
        num_pit_stops=0,
        current_lap_invalid=0,
        delta_to_car_in_front_ms_part=0,
        delta_to_car_in_front_minutes_part=0,
        delta_to_race_leader_ms_part=0,
        delta_to_race_leader_minutes_part=0,
    )
    return SimpleNamespace(
        header=SimpleNamespace(session_time=time), lap_data=[lap_data]
    )


def index_with(*, status=None, laps=None):
    car = SimpleNamespace(car_status=status or [], lap_data=laps or [])
    return cast(Index, SimpleNamespace(cars={0: car}))


def test_status_samples_and_status_at_use_latest_sample_at_or_before_time():
    index = index_with(status=[status_packet(10.0, 0, 1), status_packet(20.0, 1, 0)])

    assert _status_samples(index, 0) == [(10.0, 0, 1), (20.0, 1, 0)]
    assert _status_at(index, 0, 9.9) is None
    assert _status_at(index, 0, 10.0) == (0, 1)
    assert _status_at(index, 0, 19.9) == (0, 1)
    assert _status_at(index, 0, 20.0) == (1, 0)
    assert _status_at(index, 0, 21.0) == (1, 0)


def test_status_at_returns_none_when_there_are_no_samples():
    assert _status_at(index_with(), 0, 10.0) is None


def test_tyre_strategy_starts_stints_on_compound_change_or_age_reset():
    index = index_with(
        status=[
            status_packet(0.0, 0, 0),
            status_packet(5.0, 0, 1),
            status_packet(10.0, 0, 2),
            status_packet(15.0, 0, 0),
            status_packet(20.0, 1, 1),
        ]
    )

    assert tyre_strategy(index, 0) == [
        {
            "compound": 0,
            "compound_name": "SOFT",
            "start_t": 0.0,
            "end_t": 10.0,
            "start_age_laps": 0,
            "end_age_laps": 2,
            "laps": 2,
        },
        {
            "compound": 0,
            "compound_name": "SOFT",
            "start_t": 15.0,
            "end_t": 15.0,
            "start_age_laps": 0,
            "end_age_laps": 0,
            "laps": 0,
        },
        {
            "compound": 1,
            "compound_name": "MEDIUM",
            "start_t": 20.0,
            "end_t": 20.0,
            "start_age_laps": 1,
            "end_age_laps": 1,
            "laps": 0,
        },
    ]


def test_tyre_strategy_handles_unknown_compounds_and_empty_status():
    assert tyre_strategy(index_with(), 0) == []
    assert tyre_strategy(index_with(status=[status_packet(1.0, 99, 0)]), 0) == [
        {
            "compound": 99,
            "compound_name": "UNKNOWN",
            "start_t": 1.0,
            "end_t": 1.0,
            "start_age_laps": 0,
            "end_age_laps": 0,
            "laps": 0,
        }
    ]


def test_tyre_degradation_groups_valid_completed_laps_by_compound_and_sorts_age():
    index = index_with(
        status=[
            status_packet(0.0, 0, 5),
            status_packet(20.0, 0, 3),
            status_packet(30.0, 1, 1),
        ],
        laps=[
            lap_packet(15.0, 2, 95000),
            lap_packet(25.0, 3, 90000),
            lap_packet(35.0, 4, 0),
        ],
    )

    assert tyre_degradation(index, 0) == {
        0: [
            {"lap": 2, "lap_time_ms": 90000, "tyres_age_laps": 3},
            {"lap": 1, "lap_time_ms": 95000, "tyres_age_laps": 5},
        ],
    }


def test_tyre_degradation_groups_laps_after_compound_change():
    index = index_with(
        status=[status_packet(0.0, 0, 0), status_packet(20.0, 1, 1)],
        laps=[lap_packet(15.0, 2, 95000), lap_packet(25.0, 3, 90000)],
    )

    assert tyre_degradation(index, 0) == {
        0: [{"lap": 1, "lap_time_ms": 95000, "tyres_age_laps": 0}],
        1: [{"lap": 2, "lap_time_ms": 90000, "tyres_age_laps": 1}],
    }


def test_tyre_degradation_ignores_laps_without_a_prior_status():
    index = index_with(
        status=[status_packet(10.0, 0, 0)],
        laps=[lap_packet(5.0, 2, 90000)],
    )

    assert tyre_degradation(index, 0) == {}


def test_tyre_degradation_ignores_laps_without_a_lap_time():
    index = index_with(
        status=[status_packet(0.0, 0, 0)],
        laps=[lap_packet(5.0, 2, None)],
    )

    assert tyre_degradation(index, 0) == {}
