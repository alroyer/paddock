from telemetry.packet.header import PacketHeader
from telemetry.packet.lobby import LobbyInfoData, PacketLobbyInfoData


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


def test_lobby_info_roundtrip():
    li = LobbyInfoData(
        ai_controlled=0,
        team_id=5,
        nationality=9,
        platform=1,
        name="LobbyPlayer",
        car_number=44,
        your_telemetry=1,
        show_online_names=0,
        tech_level=1234,
        ready_status=1,
    )
    b = li.to_bytes()
    assert len(b) == LobbyInfoData.SIZE
    li2 = LobbyInfoData.from_bytes(b)
    assert li2.name.startswith("LobbyPlayer")
    assert li2.team_id == li.team_id


def test_packet_lobby_roundtrip():
    hdr = _make_header()
    one = LobbyInfoData(
        ai_controlled=1,
        team_id=2,
        nationality=3,
        platform=4,
        name="P",
        car_number=7,
        your_telemetry=0,
        show_online_names=1,
        tech_level=4321,
        ready_status=2,
    )
    pkt = PacketLobbyInfoData(header=hdr, num_players=10, lobby_players=[one] * 22)
    b = pkt.to_bytes()
    assert len(b) == PacketLobbyInfoData.SIZE
    header, remaining = PacketHeader.parse(b)
    pkt2, remaining = PacketLobbyInfoData.parse(header, remaining)
    assert remaining == b""
    assert pkt2.num_players == 10
    assert len(pkt2.lobby_players) == 22
    assert pkt2.lobby_players[0].car_number == one.car_number
