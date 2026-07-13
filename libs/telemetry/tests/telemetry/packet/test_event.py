import math

from helpers import make_header
from telemetry.packet.event import EventDataDetails, PacketEventData
from telemetry.packet.header import PacketHeader


def test_packet_event_data_size():
    assert PacketEventData.SIZE == 45


def test_fastest_lap_roundtrip():
    hdr = make_header(0)
    details = EventDataDetails.from_fastest_lap(5, 78.912)
    pkt = PacketEventData(header=hdr, event_string_code=b"FTLP", event_details=details)
    b = pkt.to_bytes()
    assert len(b) == PacketEventData.SIZE
    header, remaining = PacketHeader.parse(b)
    pkt2, remaining = PacketEventData.parse(header, remaining)
    assert remaining == b""
    assert math.isclose(pkt2.header.session_time, pkt.header.session_time, rel_tol=1e-6)
    assert pkt2.event_string_code == b"FTLP"
    v_idx, lap = pkt2.event_details.as_fastest_lap()
    assert v_idx == 5
    assert math.isclose(lap, 78.912, rel_tol=1e-6)
    assert pkt2.event_name() == "Fastest Lap"


def test_speed_trap_roundtrip():
    hdr = make_header(1)
    details = EventDataDetails.from_speed_trap(3, 320.5, 1, 0, 7, 322.1)
    pkt = PacketEventData(header=hdr, event_string_code=b"SPTP", event_details=details)
    b = pkt.to_bytes()
    assert len(b) == PacketEventData.SIZE
    header, remaining = PacketHeader.parse(b)
    pkt2, remaining = PacketEventData.parse(header, remaining)
    assert remaining == b""
    assert pkt2.event_string_code == b"SPTP"
    v_idx, speed, is_overall, is_driver, fastest_idx, fastest_speed = (
        pkt2.event_details.as_speed_trap()
    )
    assert v_idx == 3
    assert is_overall == 1
    assert is_driver == 0
    assert fastest_idx == 7
    assert math.isclose(speed, 320.5, rel_tol=1e-6)
    assert math.isclose(fastest_speed, 322.1, rel_tol=1e-6)
    assert pkt2.event_name() == "Speed Trap Triggered"


def test_flashback_roundtrip():
    hdr = make_header(2)
    details = EventDataDetails.from_flashback(123456, 45.67)
    pkt = PacketEventData(header=hdr, event_string_code=b"FLBK", event_details=details)
    b = pkt.to_bytes()
    header, remaining = PacketHeader.parse(b)
    pkt2, remaining = PacketEventData.parse(header, remaining)
    assert remaining == b""
    frame, session_time = pkt2.event_details.as_flashback()
    assert frame == 123456
    assert math.isclose(session_time, 45.67, rel_tol=1e-6)
    assert pkt2.event_name() == "Flashback"
