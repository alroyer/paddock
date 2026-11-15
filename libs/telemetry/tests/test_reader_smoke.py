"""Smoke tests: the public API imports, and decode_packet round-trips a synthetic datagram."""

import struct

import pytest
import telemetry
from telemetry import (
    DecodedPacket,
    InvalidPacketLengthError,
    PacketId,
    TelemetryPacketError,
    TruncatedPacketError,
    decode_packet,
)
from telemetry.schemas import SCHEMAS

HEADER_FORMAT = struct.Struct("<HBBBBBQfIIBB")


def _count_total(shape: int | tuple[int, ...]) -> int:
    if isinstance(shape, int):
        return shape
    total = 1
    for dimension in shape:
        total *= dimension
    return total


def _encode_record(schema_name: str) -> bytes:
    """Encode a zero-filled record following the SCHEMAS layout (no NUL-terminated names)."""
    out = bytearray()
    for name, field_type, count in SCHEMAS[schema_name]:
        if field_type in SCHEMAS:
            out += _encode_record(field_type) * count
        elif field_type == "EventDataDetails":
            out += b"\x00" * 12
        elif name == "event_string_code":
            out += b"FTLP"
        elif field_type == "s":
            out += b"paddock" + b"\x00" * max(_count_total(count) - len("paddock"), 0)
        else:
            size = struct.calcsize(f"<{field_type}")
            out += b"\x00" * (_count_total(count) * size)
    return bytes(out)


def _encode_header(packet_id: int) -> bytes:
    return HEADER_FORMAT.pack(2026, 26, 1, 0, 1, packet_id, 123456789, 12.5, 7, 42, 0, 255)


def test_public_api_is_importable() -> None:
    for name in telemetry.__all__:
        assert hasattr(telemetry, name), f"telemetry.__all__ lists {name!r} but it is not importable"


def test_decode_motion_packet_round_trip() -> None:
    datagram = _encode_header(PacketId.MOTION.value) + _encode_record("CarMotionData") * 24

    packet = decode_packet(datagram)

    assert isinstance(packet, DecodedPacket)
    assert packet.packet_id is PacketId.MOTION
    assert packet.header.session_uid == 123456789
    assert packet.header.frame_identifier == 7
    assert packet.header.player_car_index == 0
    cars = packet.payload["car_motion_data"]
    assert len(cars) == 24
    assert cars[0]["world_position_x"] == 0.0


def test_decode_event_packet() -> None:
    datagram = _encode_header(PacketId.EVENT.value) + b"FTLP" + b"\x00" * 12

    packet = decode_packet(datagram)

    event = packet.payload["event_details"]
    assert event["event_name"] == "fastest_lap"
    assert event["event_details"] == {"vehicle_idx": 0, "lap_time": 0.0}


def test_truncated_packet_raises() -> None:
    datagram = _encode_header(PacketId.MOTION.value)
    with pytest.raises(TruncatedPacketError):
        decode_packet(datagram[: len(datagram) - 1])


def test_trailing_bytes_raise() -> None:
    datagram = _encode_header(PacketId.MOTION.value) + _encode_record("CarMotionData") * 24
    with pytest.raises(InvalidPacketLengthError):
        decode_packet(datagram + b"\x00")


def test_unsupported_format_raises() -> None:
    header = HEADER_FORMAT.pack(2025, 25, 1, 0, 1, PacketId.MOTION.value, 0, 0.0, 0, 0, 0, 255)
    with pytest.raises(TelemetryPacketError):
        decode_packet(header)
