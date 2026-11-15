from __future__ import annotations

import socket
import struct
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self

from .constants import (
    MAX_ACTIVE_AERO_ZONES_PER_LAP,
    MAX_DRS_ZONES_PER_LAP,
    MAX_MARSHAL_ZONES_PER_LAP,
    MAX_NUM_CARS_IN_UDP_DATA,
    MAX_NUM_LAPS_IN_HISTORY,
    MAX_NUM_LAPS_IN_LAP_POSITIONS_HISTORY_PACKET,
    MAX_SESSIONS_IN_WEEKEND,
    MAX_TYRE_STINTS,
    MAX_WEATHER_FORECAST_SAMPLES,
)
from .enums import PacketId
from .packets import EVENT_CODES, PacketHeader
from .schemas import SCHEMAS

UDP_PORT = 20777
MAX_UDP_PACKET_SIZE = 2048
PACKET_FORMAT = 2026
PACKET_SCHEMAS = {
    PacketId.MOTION: "PacketMotionData",
    PacketId.SESSION: "PacketSessionData",
    PacketId.LAP_DATA: "PacketLapData",
    PacketId.EVENT: "PacketEventData",
    PacketId.PARTICIPANTS: "PacketParticipantsData",
    PacketId.CAR_SETUPS: "PacketCarSetupData",
    PacketId.CAR_TELEMETRY: "PacketCarTelemetryData",
    PacketId.CAR_STATUS: "PacketCarStatusData",
    PacketId.FINAL_CLASSIFICATION: "PacketFinalClassificationData",
    PacketId.LOBBY_INFO: "PacketLobbyInfoData",
    PacketId.CAR_DAMAGE: "PacketCarDamageData",
    PacketId.SESSION_HISTORY: "PacketSessionHistoryData",
    PacketId.TYRE_SETS: "PacketTyreSetsData",
    PacketId.MOTION_EX: "PacketMotionExData",
    PacketId.TIME_TRIAL: "PacketTimeTrialData",
    PacketId.LAP_POSITIONS: "PacketLapPositionsData",
    PacketId.CAR_TELEMETRY_2: "PacketCarTelemetry2Data",
}


class TelemetryPacketError(ValueError):
    """Raised when a UDP datagram is not a supported telemetry packet."""


class TruncatedPacketError(TelemetryPacketError):
    """Raised when a packet ends before a required field is available."""


class InvalidPacketLengthError(TelemetryPacketError):
    """Raised when a packet has bytes beyond its specified structure."""


class UnsupportedPacketFormatError(TelemetryPacketError):
    """Raised when a packet uses a format other than the F1 26 format."""


class UnknownPacketIdError(TelemetryPacketError):
    """Raised when a packet ID is not defined by the F1 26 specification."""


@dataclass(frozen=True)
class DecodedPacket:
    header: PacketHeader
    packet_id: PacketId
    payload: Mapping[str, object]
    source_address: tuple[str, int] | None = None


class _Cursor:
    def __init__(self, data: bytes | bytearray | memoryview) -> None:
        self._data = memoryview(data)
        self.offset = 0

    def read(self, size: int) -> bytes:
        remaining = len(self._data) - self.offset
        if size > remaining:
            raise TruncatedPacketError(
                f"Packet ended at byte {self.offset}; need {size} more bytes, but only {remaining} remain."
            )
        start = self.offset
        self.offset += size
        return self._data[start : self.offset].tobytes()

    def unpack(self, fmt: str) -> object:
        layout = struct.Struct(f"<{fmt}")
        values = layout.unpack(self.read(layout.size))
        return values[0] if len(values) == 1 else values


def _product(shape: int | tuple[int, ...]) -> int:
    if isinstance(shape, int):
        return shape
    result = 1
    for dimension in shape:
        result *= dimension
    return result


def _decode_record(cursor: _Cursor, schema_name: str, *, skip_header: bool = False) -> dict[str, object]:
    try:
        fields = SCHEMAS[schema_name]
    except KeyError as error:
        raise TelemetryPacketError(f"No binary schema is registered for {schema_name}.") from error

    record: dict[str, object] = {}
    for name, field_type, count in fields:
        if skip_header and name == "header":
            continue
        if field_type == "EventDataDetails":
            record[name] = cursor.read(12)
        elif name == "event_string_code":
            record[name] = cursor.read(count)
        elif field_type in SCHEMAS:
            if count == 1:
                record[name] = _decode_record(cursor, field_type)
            else:
                record[name] = [_decode_record(cursor, field_type) for _ in range(count)]
        elif field_type == "s":
            raw_name = cursor.read(count)
            try:
                record[name] = raw_name.split(b"\0", 1)[0].decode("utf-8")
            except UnicodeDecodeError as error:
                raise TelemetryPacketError(f"Field {name} contains invalid UTF-8.") from error
        else:
            values = cursor.unpack(f"{_product(count)}{field_type}")
            if isinstance(count, tuple):
                rows, columns = count
                flat_values = list(values)
                record[name] = [flat_values[row * columns : (row + 1) * columns] for row in range(rows)]
            elif count == 1:
                record[name] = values
            else:
                record[name] = list(values)
    return record


_EVENT_NAMES = {code: name for name, code in EVENT_CODES.items()}
_EVENT_LAYOUTS: dict[bytes, tuple[tuple[str, str], ...]] = {
    b"FTLP": (("vehicle_idx", "B"), ("lap_time", "f")),
    b"RTMT": (("vehicle_idx", "B"), ("reason", "B")),
    b"DRSD": (("reason", "B"),),
    b"TMPT": (("vehicle_idx", "B"),),
    b"RCWN": (("vehicle_idx", "B"),),
    b"PENA": (
        ("penalty_type", "B"),
        ("infringement_type", "B"),
        ("vehicle_idx", "B"),
        ("other_vehicle_idx", "B"),
        ("time", "B"),
        ("lap_num", "B"),
        ("places_gained", "B"),
    ),
    b"SPTP": (
        ("vehicle_idx", "B"),
        ("speed", "f"),
        ("is_overall_fastest_in_session", "B"),
        ("is_driver_fastest_in_session", "B"),
        ("fastest_vehicle_idx_in_session", "B"),
        ("fastest_speed_in_session", "f"),
    ),
    b"STLG": (("num_lights", "B"),),
    b"DTSV": (("vehicle_idx", "B"),),
    b"SGSV": (("vehicle_idx", "B"), ("stop_time", "f")),
    b"FLBK": (("frame_identifier", "I"), ("session_time", "f")),
    b"BUTN": (("button_status", "I"),),
    b"OVTK": (("overtaking_vehicle_idx", "B"), ("being_overtaken_vehicle_idx", "B")),
    b"SCAR": (("safety_car_type", "B"), ("event_type", "B")),
    b"COLL": (("vehicle1_idx", "B"), ("vehicle2_idx", "B"), ("severity", "B")),
}


def _decode_event(event_code: bytes, raw_details: bytes) -> dict[str, object]:
    layout = _EVENT_LAYOUTS.get(event_code)
    details = None
    if layout is not None:
        details_cursor = _Cursor(raw_details)
        details = {name: details_cursor.unpack(fmt) for name, fmt in layout}
    return {
        "event_string_code": event_code,
        "event_name": _EVENT_NAMES.get(event_code),
        "event_details": details,
        "raw_event_details": raw_details,
    }


def _validate_payload_counts(packet_id: PacketId, payload: Mapping[str, object]) -> None:
    capacities: dict[PacketId, tuple[tuple[str, int], ...]] = {
        PacketId.SESSION: (
            ("num_marshal_zones", MAX_MARSHAL_ZONES_PER_LAP),
            ("num_weather_forecast_samples", MAX_WEATHER_FORECAST_SAMPLES),
            ("num_sessions_in_weekend", MAX_SESSIONS_IN_WEEKEND),
            ("num_active_aero_zones_full", MAX_ACTIVE_AERO_ZONES_PER_LAP),
            ("num_active_aero_zones_partial", MAX_ACTIVE_AERO_ZONES_PER_LAP),
            ("num_drs_zones", MAX_DRS_ZONES_PER_LAP),
        ),
        PacketId.PARTICIPANTS: (("num_active_cars", MAX_NUM_CARS_IN_UDP_DATA),),
        PacketId.FINAL_CLASSIFICATION: (("num_cars", MAX_NUM_CARS_IN_UDP_DATA),),
        PacketId.LOBBY_INFO: (("num_players", MAX_NUM_CARS_IN_UDP_DATA),),
        PacketId.SESSION_HISTORY: (
            ("num_laps", MAX_NUM_LAPS_IN_HISTORY),
            ("num_tyre_stints", MAX_TYRE_STINTS),
        ),
        PacketId.LAP_POSITIONS: (("num_laps", MAX_NUM_LAPS_IN_LAP_POSITIONS_HISTORY_PACKET),),
    }
    for name, capacity in capacities.get(packet_id, ()):
        value = payload[name]
        if not isinstance(value, int) or value > capacity:
            raise TelemetryPacketError(f"{packet_id.name} field {name} is {value}; maximum is {capacity}.")


def decode_packet(data: bytes | bytearray | memoryview) -> DecodedPacket:
    """Decode a complete F1 26 UDP datagram into a header and payload mapping."""
    cursor = _Cursor(data)
    header_data = _decode_record(cursor, "PacketHeader")
    header = PacketHeader(**header_data)

    if header.packet_format != PACKET_FORMAT:
        raise UnsupportedPacketFormatError(f"Expected packet format {PACKET_FORMAT}, got {header.packet_format}.")

    try:
        packet_id = PacketId(header.packet_id)
    except ValueError as error:
        raise UnknownPacketIdError(f"Unknown F1 26 packet ID {header.packet_id}.") from error

    schema_name = PACKET_SCHEMAS[packet_id]
    packet_data = _decode_record(cursor, schema_name, skip_header=True)
    if packet_id is PacketId.EVENT:
        event_code = packet_data["event_string_code"]
        event_details = packet_data["event_details"]
        if not isinstance(event_code, bytes) or not isinstance(event_details, bytes):
            raise TelemetryPacketError("Invalid event packet schema.")
        packet_data["event_string_code"] = event_code
        packet_data["event_details"] = _decode_event(event_code, event_details)

    if cursor.offset != len(cursor._data):
        raise InvalidPacketLengthError(
            f"Packet {packet_id.name} decoded {cursor.offset} bytes, "
            f"but the datagram contains {len(cursor._data)} bytes."
        )

    _validate_payload_counts(packet_id, packet_data)
    return DecodedPacket(header, packet_id, packet_data)


class TelemetryReceiver:
    """Bind a UDP socket and decode incoming F1 26 telemetry datagrams."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = UDP_PORT,
        *,
        timeout: float | None = None,
    ) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self._socket.settimeout(timeout)
            self._socket.bind((host, port))
        except (OSError, ValueError):
            self._socket.close()
            raise

    @property
    def address(self) -> tuple[str, int]:
        """Return the local address, including the assigned port."""
        host, port = self._socket.getsockname()
        return host, port

    def receive(self) -> DecodedPacket:
        """Receive and decode one datagram; socket timeouts/errors propagate."""
        data, sender = self._socket.recvfrom(MAX_UDP_PACKET_SIZE)
        packet = decode_packet(data)
        return DecodedPacket(
            packet.header,
            packet.packet_id,
            packet.payload,
            (sender[0], sender[1]),
        )

    def close(self) -> None:
        self._socket.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
