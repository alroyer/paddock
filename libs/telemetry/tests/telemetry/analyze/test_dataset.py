from types import SimpleNamespace
from typing import cast

import pytest
from telemetry.analyze import dataset as dataset_mod
from telemetry.analyze.dataset import TelemetryDataset
from telemetry.analyze.index import Index


def make_index(*, n_cars: int = 2, participants=None):
    return cast(
        Index,
        SimpleNamespace(
            cars={ci: SimpleNamespace() for ci in range(n_cars)},
            participants=participants or [],
            n_cars=n_cars,
            player_car_index=1,
        ),
    )


def make_participant(name: str, race_number: int, team_id: int):
    return SimpleNamespace(name=name, race_number=race_number, team_id=team_id)


def make_dataset(index=None):
    dataset = TelemetryDataset.__new__(TelemetryDataset)
    dataset._index = index or make_index()
    return dataset


def test_init_builds_and_exposes_the_index(monkeypatch):
    index = make_index()
    packets = [object()]
    monkeypatch.setattr(dataset_mod, "build_index", lambda value: index)

    dataset = TelemetryDataset(packets)

    assert dataset.index is index


def test_from_file_loads_packets_and_builds_dataset(monkeypatch, tmp_path):
    path = tmp_path / "session.bin"
    path.write_bytes(b"")
    packets = [object()]
    index = make_index()
    loaded_paths = []

    def load(path_arg):
        loaded_paths.append(path_arg)
        return packets

    monkeypatch.setattr(dataset_mod, "load_telemetry", load)
    monkeypatch.setattr(dataset_mod, "build_index", lambda value: index)

    dataset = TelemetryDataset.from_file(path)

    assert loaded_paths == [path]
    assert dataset.index is index


def test_cars_returns_participant_metadata_and_best_lap(monkeypatch):
    participants = [
        SimpleNamespace(
            participants=[
                make_participant("Alice", 7, 10),
                make_participant("Bob", 22, 20),
            ]
        )
    ]
    dataset = make_dataset(make_index(participants=participants))
    best_laps = {0: 91234, 1: None}
    monkeypatch.setattr(
        dataset_mod.laps_mod,
        "best_lap_ms",
        lambda index, ci: best_laps[ci],
    )

    assert dataset.cars() == [
        {
            "car_idx": 0,
            "name": "Alice",
            "race_number": 7,
            "team_id": 10,
            "is_player": False,
            "best_lap_ms": 91234,
        },
        {
            "car_idx": 1,
            "name": "Bob",
            "race_number": 22,
            "team_id": 20,
            "is_player": True,
            "best_lap_ms": None,
        },
    ]


def test_car_updates_best_lap_and_falls_back_when_participant_is_missing(
    monkeypatch,
):
    dataset = make_dataset(make_index(n_cars=1))
    monkeypatch.setattr(dataset_mod, "resolve_car", lambda index, ref: ref)
    monkeypatch.setattr(
        TelemetryDataset,
        "best_laps",
        lambda self, ref: [{"lap_time_ms": 85432}],
    )

    assert dataset.car(0) == {
        "car_idx": 0,
        "name": "car_0",
        "race_number": None,
        "team_id": None,
        "is_player": False,
        "best_lap_ms": 85432,
    }


def test_laps_applies_limit_to_the_latest_laps(monkeypatch):
    dataset = make_dataset()
    monkeypatch.setattr(dataset_mod, "resolve_car", lambda index, ref: 0)
    source_laps = [{"lap": 1}, {"lap": 2}, {"lap": 3}]
    monkeypatch.setattr(
        dataset_mod.laps_mod, "lap_summaries", lambda index, ci: source_laps
    )

    assert dataset.laps("Alice", limit=2) == [{"lap": 2}, {"lap": 3}]
    assert dataset.laps("Alice") is source_laps


def test_best_laps_filters_nonpositive_times_sorts_and_limits(monkeypatch):
    dataset = make_dataset()
    monkeypatch.setattr(dataset_mod, "resolve_car", lambda index, ref: 0)
    monkeypatch.setattr(
        TelemetryDataset,
        "laps",
        lambda self, ref: [
            {"lap": 1, "lap_time_ms": 0},
            {"lap": 2, "lap_time_ms": 95000},
            {"lap": 3, "lap_time_ms": -1},
            {"lap": 4, "lap_time_ms": 91000},
        ],
    )

    assert dataset.best_laps("Alice", limit=1) == [{"lap": 4, "lap_time_ms": 91000}]


@pytest.mark.parametrize(
    ("method_name", "module_name", "function_name", "arguments", "result"),
    [
        ("sector_breakdown", "laps_mod", "sector_breakdown", (3,), {"sector": 1}),
        ("compare_laps", "laps_mod", "compare_laps", (3, 4), {"delta": 2}),
        ("speed_trace", "driving", "speed_trace", (), [(1.0, 100.0)]),
        ("gear_usage", "driving", "gear_usage", (), [{"gear": 6}]),
        ("fuel_profile", "fuel", "fuel_profile", (), {"consumption": 1.2}),
        ("ers_usage", "ers", "ers_usage", (), {"deploy": 3}),
        ("tyre_strategy", "tyres", "tyre_strategy", (), [{"compound": 0}]),
        ("tyre_degradation", "tyres", "tyre_degradation", (), {0: []}),
        ("pit_stops", "strategy", "pit_stops", (), [{"lap": 12}]),
        ("position_changes", "strategy", "position_changes", (), [{"delta": 1}]),
    ],
)
def test_analysis_methods_resolve_car_and_delegate(
    monkeypatch, method_name, module_name, function_name, arguments, result
):
    dataset = make_dataset()
    calls = []
    monkeypatch.setattr(dataset_mod, "resolve_car", lambda index, ref: 4)

    if method_name == "speed_trace" or method_name == "fuel_profile":
        arguments = (240,)

    def delegate(*args):
        calls.append(args)
        return result

    monkeypatch.setattr(getattr(dataset_mod, module_name), function_name, delegate)

    assert getattr(dataset, method_name)("Alice", *arguments) == result
    assert calls == [(dataset.index, 4, *arguments)]


def test_board_delegates_without_car_resolution(monkeypatch):
    dataset = make_dataset()
    result = [{"position": 1}]
    calls = []
    monkeypatch.setattr(
        dataset_mod,
        "session_board",
        lambda index: calls.append(index) or result,
    )

    assert dataset.board() == result
    assert calls == [dataset.index]
