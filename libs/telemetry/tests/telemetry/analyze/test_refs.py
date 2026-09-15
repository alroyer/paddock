from types import SimpleNamespace
from typing import cast

import pytest
from telemetry.analyze.index import Index
from telemetry.analyze.refs import _car_active, _known_names, resolve_car
from telemetry.analyze.types import UnknownCar


def participant_packet(*names, num_active_cars=None):
    participants = [SimpleNamespace(name=name) for name in names]
    return SimpleNamespace(
        participants=participants,
        num_active_cars=num_active_cars if num_active_cars is not None else len(names),
    )


def index_with(*, n_cars=2, participant_packets=None, car_indices=None):
    indices = range(n_cars) if car_indices is None else car_indices
    return cast(
        Index,
        SimpleNamespace(
            cars={ci: SimpleNamespace() for ci in indices},
            n_cars=n_cars,
            participants=participant_packets or [],
        ),
    )


def test_car_active_checks_the_upper_car_limit():
    index = index_with(n_cars=2)

    assert _car_active(index, 0) is True
    assert _car_active(index, 1) is True
    assert _car_active(index, 2) is False


def test_resolve_car_accepts_an_active_integer_index():
    index = index_with(n_cars=2)

    assert resolve_car(index, 1) == 1


@pytest.mark.parametrize("reference", [2, 4])
def test_resolve_car_rejects_missing_or_inactive_integer_index(reference):
    index = index_with(n_cars=2, car_indices=[0, 1] if reference == 2 else [4])

    with pytest.raises(UnknownCar, match=rf"no telemetry for car_idx {reference}"):
        resolve_car(index, reference)


def test_resolve_car_matches_driver_names_case_insensitively_and_trimmed():
    index = index_with(
        participant_packets=[participant_packet("Alice", "Max Verstappen")]
    )

    assert resolve_car(index, "  aLiCe ") == 0
    assert resolve_car(index, "MAX VERSTAPPEN") == 1


def test_resolve_car_rejects_empty_and_unknown_names():
    index = index_with(participant_packets=[participant_packet("Alice")])

    with pytest.raises(UnknownCar, match="empty car name"):
        resolve_car(index, "   ")
    with pytest.raises(UnknownCar, match=r"unknown driver 'Bob' \(known: Alice\)"):
        resolve_car(index, "Bob")


def test_known_names_handles_missing_participants_and_active_car_limit():
    assert _known_names(index_with()) == "none"

    index = index_with(
        n_cars=2,
        participant_packets=[participant_packet("Alice", "Bob", "Charlie")],
    )
    assert _known_names(index) == "Alice, Bob"
