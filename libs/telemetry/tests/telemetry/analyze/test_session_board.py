from types import SimpleNamespace
from typing import cast

from telemetry.analyze import session_board as board_mod
from telemetry.analyze.index import Index


def participant_packet(*names):
    return SimpleNamespace(participants=[SimpleNamespace(name=name) for name in names])


def classification_entry(
    position: int,
    num_laps: int,
    best_lap_time: int,
    pit_stops: int,
    result_status: int,
):
    return SimpleNamespace(
        position=position,
        num_laps=num_laps,
        best_lap_time_in_ms=best_lap_time,
        num_pit_stops=pit_stops,
        result_status=result_status,
    )


def index_with(*, n_cars=2, participants=None, classification=None):
    return cast(
        Index,
        SimpleNamespace(
            n_cars=n_cars,
            participants=participants or [],
            final_classification=classification,
            cars={ci: SimpleNamespace() for ci in range(n_cars)},
        ),
    )


def test_session_board_uses_final_classification_sorts_and_falls_back_names():
    classification = SimpleNamespace(
        classification_data=[
            classification_entry(2, 20, 0, 1, 4),
            classification_entry(1, 21, 87654, 2, 3),
        ]
    )
    index = index_with(
        participants=[participant_packet("Alice")],
        classification=classification,
    )

    assert board_mod.session_board(index) == [
        {
            "position": 1,
            "car_idx": 1,
            "name": "car_1",
            "num_laps": 21,
            "best_lap_ms": 87654,
            "num_pit_stops": 2,
            "result_status": 3,
        },
        {
            "position": 2,
            "car_idx": 0,
            "name": "Alice",
            "num_laps": 20,
            "best_lap_ms": None,
            "num_pit_stops": 1,
            "result_status": 4,
        },
    ]


def test_session_board_falls_back_to_last_completed_laps(monkeypatch):
    completed = {
        0: [
            {"position": 4, "num_pit_stops": 0},
            {"position": 2, "num_pit_stops": 1},
        ],
        1: [],
        2: [{"position": 6, "num_pit_stops": 3}],
    }
    best_times = {0: 90000, 2: None}
    monkeypatch.setattr(board_mod, "_completed_laps", lambda index, ci: completed[ci])
    monkeypatch.setattr(board_mod, "best_lap_ms", lambda index, ci: best_times[ci])
    index = index_with(
        n_cars=3,
        participants=[participant_packet("Alice", "Bob", "Charlie")],
    )

    assert board_mod.session_board(index) == [
        {
            "position": 2,
            "car_idx": 0,
            "name": "Alice",
            "num_laps": 2,
            "best_lap_ms": 90000,
            "num_pit_stops": 1,
            "result_status": None,
        },
        {
            "position": 6,
            "car_idx": 2,
            "name": "Charlie",
            "num_laps": 1,
            "best_lap_ms": None,
            "num_pit_stops": 3,
            "result_status": None,
        },
    ]


def test_session_board_is_empty_without_classification_or_completed_laps():
    index = index_with()
    for car in index.cars.values():
        car.lap_data = []

    assert board_mod.session_board(index) == []
