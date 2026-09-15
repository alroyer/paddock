from types import SimpleNamespace

import pytest
from telemetry.analyze import index as index_mod
from telemetry.analyze.index import CarIndex, build_index


def header(time: float, packet_id: int):
    return SimpleNamespace(
        session_time=time,
        packet_id=packet_id,
        session_uid=123,
        game_year=2025,
        player_car_index=1,
    )


def packet(packet_type, time: float, packet_id: int, **attributes):
    value = packet_type.__new__(packet_type)
    value.header = header(time, packet_id)
    for name, attribute in attributes.items():
        setattr(value, name, attribute)
    return value


def test_car_index_starts_with_empty_packet_lists():
    car = CarIndex()

    assert car.motion == []
    assert car.car_telemetry == []
    assert car.car_status == []
    assert car.lap_data == []
    assert car.tyre_sets == []


def test_build_index_rejects_empty_packet_list():
    with pytest.raises(ValueError, match="no packets to index"):
        build_index([])


def test_build_index_groups_all_packet_types_and_keeps_metadata(monkeypatch):
    packet_types = {
        name: type(name, (), {})
        for name in (
            "PacketMotionData",
            "PacketCarTelemetryData",
            "PacketCarStatusData",
            "PacketLapData",
            "PacketTyreSetsData",
            "PacketEventData",
            "PacketParticipantsData",
            "PacketSessionData",
            "PacketFinalClassificationData",
        )
    }
    for name, packet_type in packet_types.items():
        monkeypatch.setattr(index_mod, name, packet_type)

    motion = packet(
        packet_types["PacketMotionData"],
        8.0,
        1,
        car_motion_data=["motion-0", "motion-1"],
    )
    telemetry = packet(
        packet_types["PacketCarTelemetryData"],
        3.0,
        2,
        car_telemetry_data=["telemetry-0", "telemetry-1"],
    )
    status = packet(
        packet_types["PacketCarStatusData"],
        4.0,
        3,
        car_status_data=["status-0", "status-1"],
    )
    laps = packet(
        packet_types["PacketLapData"],
        5.0,
        4,
        lap_data=["lap-0", "lap-1"],
    )
    tyre_sets = packet(
        packet_types["PacketTyreSetsData"],
        6.0,
        5,
        car_idx=1,
    )
    event = packet(packet_types["PacketEventData"], 7.0, 6)
    participants = packet(
        packet_types["PacketParticipantsData"],
        2.0,
        7,
        participants=["Alice", "Bob"],
        num_active_cars=2,
    )
    first_session = packet(packet_types["PacketSessionData"], 1.0, 8)
    second_session = packet(packet_types["PacketSessionData"], 9.0, 8)
    first_classification = packet(
        packet_types["PacketFinalClassificationData"], 10.0, 9
    )
    second_classification = packet(
        packet_types["PacketFinalClassificationData"], 11.0, 9
    )
    unknown = packet(type("UnknownPacket", (), {}), 12.0, 10)

    result = build_index(
        [
            first_session,
            motion,
            telemetry,
            status,
            laps,
            tyre_sets,
            event,
            participants,
            second_session,
            first_classification,
            second_classification,
            unknown,
        ]
    )

    assert result.cars[0].motion == [motion]
    assert result.cars[1].motion == [motion]
    assert result.cars[0].car_telemetry == [telemetry]
    assert result.cars[1].car_status == [status]
    assert result.cars[0].lap_data == [laps]
    assert result.cars[1].tyre_sets == [tyre_sets]
    assert result.events == [event]
    assert result.participants == [participants]
    assert result.session is first_session
    assert result.final_classification is first_classification
    assert result.n_cars == 2
    assert result.session_uid == 123
    assert result.game_year == 2025
    assert result.player_car_index == 1
    assert result.t_min == 1.0
    assert result.t_max == 12.0
    assert result.packet_counts == {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 2,
        9: 2,
        10: 1,
    }


def test_build_index_uses_car_count_when_participants_are_missing(monkeypatch):
    motion_type = type("PacketMotionData", (), {})
    monkeypatch.setattr(index_mod, "PacketMotionData", motion_type)
    motion = packet(
        motion_type,
        1.0,
        1,
        car_motion_data=["motion-0", "motion-1", "motion-2"],
    )

    result = build_index([motion])

    assert result.n_cars == 3
