from telemetry.packet.header import PacketHeader
from telemetry.packet.participants import (
    LiveryColour,
    PacketParticipantsData,
    ParticipantData,
)


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


def test_participant_roundtrip():
    p = ParticipantData(
        ai_controlled=1,
        driver_id=12,
        network_id=34,
        team_id=5,
        my_team=1,
        race_number=44,
        nationality=7,
        name="Test Driver",
        your_telemetry=1,
        show_online_names=0,
        tech_level=1234,
        platform=1,
        num_colours=2,
        livery_colours=[
            LiveryColour(10, 20, 30),
            LiveryColour(40, 50, 60),
            LiveryColour(70, 80, 90),
            LiveryColour(0, 0, 0),
        ],
    )

    b = p.to_bytes()
    assert len(b) == ParticipantData.SIZE
    p2 = ParticipantData.from_bytes(b)
    assert p2.ai_controlled == p.ai_controlled
    assert p2.driver_id == p.driver_id
    assert p2.team_id == p.team_id
    assert p2.name.startswith("Test Driver")
    assert p2.tech_level == p.tech_level
    assert len(p2.livery_colours) == 4
    assert p2.livery_colours[0].red == 10


def test_packet_participants_roundtrip():
    hdr = _make_header()
    one = ParticipantData(
        ai_controlled=0,
        driver_id=1,
        network_id=2,
        team_id=3,
        my_team=0,
        race_number=7,
        nationality=9,
        name="Driver X",
        your_telemetry=0,
        show_online_names=1,
        tech_level=4321,
        platform=4,
        num_colours=4,
        livery_colours=[LiveryColour(1, 2, 3)] * 4,
    )
    pkt = PacketParticipantsData(
        header=hdr, num_active_cars=22, participants=[one] * 22
    )
    b = pkt.to_bytes()
    assert len(b) == PacketParticipantsData.SIZE
    header, remaining = PacketHeader.parse(b)
    pkt2, remaining = PacketParticipantsData.parse(header, remaining)
    assert remaining == b""
    assert pkt2.num_active_cars == 22
    assert len(pkt2.participants) == 22
    assert pkt2.participants[0].name.startswith("Driver X")
