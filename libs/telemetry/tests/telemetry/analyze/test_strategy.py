from telemetry.analyze import strategy as strategy_mod


def test_pit_stops_detect_counter_increases_and_format_status_names(monkeypatch):
    laps = [
        {
            "lap": 1,
            "t_session": 60.0,
            "num_pit_stops": 0,
            "pit_status": 0,
            "lap_time_ms": 90000,
        },
        {
            "lap": 2,
            "t_session": 120.0,
            "num_pit_stops": 1,
            "pit_status": 2,
            "lap_time_ms": 95000,
        },
        {
            "lap": 3,
            "t_session": 180.0,
            "num_pit_stops": 1,
            "pit_status": 1,
            "lap_time_ms": 91000,
        },
        {
            "lap": 4,
            "t_session": 240.0,
            "num_pit_stops": 2,
            "pit_status": 99,
            "lap_time_ms": 100000,
        },
    ]
    monkeypatch.setattr(strategy_mod, "_completed_laps", lambda index, ci: laps)

    assert strategy_mod.pit_stops(object(), 0) == [
        {
            "lap": 2,
            "t_session": 120.0,
            "pit_stop_number": 1,
            "pit_status": 2,
            "pit_status_name": "OUT",
            "lap_time_ms": 95000,
        },
        {
            "lap": 4,
            "t_session": 240.0,
            "pit_stop_number": 2,
            "pit_status": 99,
            "pit_status_name": "UNKNOWN",
            "lap_time_ms": 100000,
        },
    ]


def test_pit_stops_returns_empty_when_no_completed_lap_increases_stop_count(
    monkeypatch,
):
    laps = [
        {"lap": 1, "num_pit_stops": 0},
        {"lap": 2, "num_pit_stops": 0},
    ]
    monkeypatch.setattr(strategy_mod, "_completed_laps", lambda index, ci: laps)

    assert strategy_mod.pit_stops(object(), 0) == []


def test_position_changes_reports_gains_and_losses_and_ignores_nonpositive_positions(
    monkeypatch,
):
    laps = [
        {"lap": 1, "t_session": 10.0, "position": 0},
        {"lap": 2, "t_session": 20.0, "position": 5},
        {"lap": 3, "t_session": 30.0, "position": 3},
        {"lap": 4, "t_session": 40.0, "position": -1},
        {"lap": 5, "t_session": 50.0, "position": 2},
        {"lap": 6, "t_session": 60.0, "position": 2},
    ]
    monkeypatch.setattr(strategy_mod, "_completed_laps", lambda index, ci: laps)

    assert strategy_mod.position_changes(object(), 0) == [
        {
            "lap": 3,
            "t_session": 30.0,
            "from": 5,
            "to": 3,
            "delta": -2,
        },
        {
            "lap": 5,
            "t_session": 50.0,
            "from": 3,
            "to": 2,
            "delta": -1,
        },
    ]


def test_position_changes_returns_empty_without_completed_laps(monkeypatch):
    monkeypatch.setattr(strategy_mod, "_completed_laps", lambda index, ci: [])

    assert strategy_mod.position_changes(object(), 0) == []
