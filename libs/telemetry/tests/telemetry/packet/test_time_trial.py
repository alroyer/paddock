from telemetry.packet.header import PacketHeader
from telemetry.packet.time_trial import PacketTimeTrialData, TimeTrialDataSet


def _make_header():
    return PacketHeader(
        2025,
        25,
        1,
        0,
        1,
        0,
        1234567890123456789,
        12.34,
        100,
        1000,
        0,
        255,
    )


def test_time_trial_data_set_roundtrip():
    data_set = TimeTrialDataSet(
        car_idx=1,
        team_id=7,
        lap_time_in_ms=91234,
        sector1_time_in_ms=31000,
        sector2_time_in_ms=30000,
        sector3_time_in_ms=30234,
        traction_control=1,
        gearbox_assist=0,
        anti_lock_brakes=1,
        equal_car_performance=0,
        custom_setup=1,
        valid=1,
    )
    b = data_set.to_bytes()
    assert len(b) == TimeTrialDataSet.SIZE
    data_set2 = TimeTrialDataSet.from_bytes(b)
    assert data_set2.car_idx == data_set.car_idx
    assert data_set2.lap_time_in_ms == data_set.lap_time_in_ms


def test_packet_time_trial_data_roundtrip():
    header = _make_header()
    data_set = TimeTrialDataSet(
        car_idx=1,
        team_id=7,
        lap_time_in_ms=91234,
        sector1_time_in_ms=31000,
        sector2_time_in_ms=30000,
        sector3_time_in_ms=30234,
        traction_control=1,
        gearbox_assist=0,
        anti_lock_brakes=1,
        equal_car_performance=0,
        custom_setup=1,
        valid=1,
    )
    packet = PacketTimeTrialData(
        header=header,
        player_session_best_data_set=data_set,
        personal_best_data_set=data_set,
        rival_data_set=data_set,
    )
    b = packet.to_bytes()
    assert len(b) == PacketTimeTrialData.SIZE
    packet2 = PacketTimeTrialData.from_bytes(b)
    assert packet2.header.packet_format == header.packet_format
    assert packet2.player_session_best_data_set.team_id == data_set.team_id
    assert packet2.personal_best_data_set.valid == data_set.valid
    assert packet2.rival_data_set.lap_time_in_ms == data_set.lap_time_in_ms
