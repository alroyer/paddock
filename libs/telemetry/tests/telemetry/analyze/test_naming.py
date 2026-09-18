import pytest
from telemetry.analyze.naming import TYRE_COMPOUND, PIT_STATUS, tyre_compound_name, pit_status_name


def test_tyre_compound_constants():
    expected = {
        0: "SOFT",
        1: "MEDIUM",
        2: "HARD",
        3: "INTERMEDIATE",
        4: "WET",
        5: "UNKNOWN",
    }

    assert TYRE_COMPOUND == expected


def test_tyre_compound_name_returns_correct_names():
    assert tyre_compound_name(0) == "SOFT"
    assert tyre_compound_name(1) == "MEDIUM"
    assert tyre_compound_name(2) == "HARD"
    assert tyre_compound_name(3) == "INTERMEDIATE"
    assert tyre_compound_name(4) == "WET"
    assert tyre_compound_name(5) == "UNKNOWN"
    assert tyre_compound_name(10) == "UNKNOWN"  # Unknown compound
    assert tyre_compound_name(-1) == "UNKNOWN"  # Negative compound


def test_pit_status_constants():
    expected = {
        0: "NONE",
        1: "IN",
        2: "OUT",
        3: "SERVED",
        4: "SHOULD_SERVE",
        5: "NOT_SERVED",
    }

    assert PIT_STATUS == expected


def test_pit_status_name_returns_correct_names():
    assert pit_status_name(0) == "NONE"
    assert pit_status_name(1) == "IN"
    assert pit_status_name(2) == "OUT"
    assert pit_status_name(3) == "SERVED"
    assert pit_status_name(4) == "SHOULD_SERVE"
    assert pit_status_name(5) == "NOT_SERVED"
    assert pit_status_name(10) == "UNKNOWN"  # Unknown status
    assert pit_status_name(-1) == "UNKNOWN"  # Negative status