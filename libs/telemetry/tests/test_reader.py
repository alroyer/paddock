# import socket
# import struct

# import pytest
# from telemetry import (
#     DriverId,
#     InvalidPacketLengthError,
#     NationalityId,
#     PacketId,
#     TelemetryPacketError,
#     TelemetryReceiver,
#     TeamId,
#     TruncatedPacketError,
#     TrackId,
#     UnknownPacketIdError,
#     UnsupportedPacketFormatError,
#     decode_packet,
# )
# from telemetry.reader import PACKET_SCHEMAS
# from telemetry.schemas import SCHEMAS

# HEADER_FORMAT = struct.Struct("<HBBBBBQfIIBB")
# PACKET_SIZES = {
#     PacketId.MOTION: 1325,
#     PacketId.SESSION: 926,
#     PacketId.LAP_DATA: 1399,
#     PacketId.EVENT: 45,
#     PacketId.PARTICIPANTS: 1470,
#     PacketId.CAR_SETUPS: 1233,
#     PacketId.CAR_TELEMETRY: 1448,
#     PacketId.CAR_STATUS: 1445,
#     PacketId.FINAL_CLASSIFICATION: 1134,
#     PacketId.LOBBY_INFO: 1062,
#     PacketId.CAR_DAMAGE: 1133,
#     PacketId.SESSION_HISTORY: 1460,
#     PacketId.TYRE_SETS: 231,
#     PacketId.MOTION_EX: 273,
#     PacketId.TIME_TRIAL: 104,
#     PacketId.LAP_POSITIONS: 1231,
#     PacketId.CAR_TELEMETRY_2: 269,
# }


# def make_packet(packet_id: PacketId, total_size: int | None = None) -> bytes:
#     schema_name = PACKET_SCHEMAS[packet_id]
#     size = PACKET_SIZES[packet_id] if total_size is None else total_size
#     header = HEADER_FORMAT.pack(
#         2026,
#         26,
#         1,
#         0,
#         1,
#         packet_id.value,
#         123,
#         1.5,
#         42,
#         43,
#         0,
#         255,
#     )
#     assert len(header) == 29
#     assert schema_name in SCHEMAS
#     return header + bytes(size - len(header))


# @pytest.mark.parametrize(("packet_id", "expected_size"), PACKET_SIZES.items())
# def test_decodes_every_packet_type(packet_id: PacketId, expected_size: int) -> None:
#     packet = decode_packet(make_packet(packet_id, expected_size))

#     assert packet.packet_id is packet_id
#     assert packet.header.packet_format == 2026
#     assert packet.header.session_uid == 123
#     assert packet.payload


# def test_decodes_car_telemetry_values() -> None:
#     data = bytearray(make_packet(PacketId.CAR_TELEMETRY))
#     struct.pack_into("<H", data, 29, 321)

#     packet = decode_packet(data)

#     cars = packet.payload["car_telemetry_data"]
#     assert isinstance(cars, list)
#     assert cars[0]["speed"] == 321


# def test_decodes_event_code_and_payload() -> None:
#     data = bytearray(make_packet(PacketId.EVENT))
#     data[29:33] = b"FTLP"
#     struct.pack_into("<Bf", data, 33, 4, 91.25)

#     packet = decode_packet(data)

#     assert packet.payload["event_string_code"] == b"FTLP"
#     event = packet.payload["event_details"]
#     assert event["event_name"] == "fastest_lap"
#     assert event["event_details"] == {"vehicle_idx": 4, "lap_time": 91.25}


# def test_rejects_truncated_and_oversized_packets() -> None:
#     packet = make_packet(PacketId.CAR_TELEMETRY)

#     with pytest.raises(TruncatedPacketError):
#         decode_packet(packet[:-1])

#     with pytest.raises(InvalidPacketLengthError):
#         decode_packet(packet + b"\0")


# def test_rejects_unsupported_format_and_unknown_id() -> None:
#     data = bytearray(make_packet(PacketId.MOTION))
#     struct.pack_into("<H", data, 0, 2025)
#     with pytest.raises(UnsupportedPacketFormatError):
#         decode_packet(data)

#     data = bytearray(make_packet(PacketId.MOTION))
#     data[6] = 255
#     with pytest.raises(UnknownPacketIdError):
#         decode_packet(data)


# def test_rejects_counts_beyond_fixed_array_capacity() -> None:
#     data = bytearray(make_packet(PacketId.PARTICIPANTS))
#     data[29] = 25

#     with pytest.raises(TelemetryPacketError, match="num_active_cars"):
#         decode_packet(data)


# def test_udp_receiver_decodes_datagrams_and_reports_sender() -> None:
#     with (
#         TelemetryReceiver("127.0.0.1", 0, timeout=1) as receiver,
#         socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender,
#     ):
#         sender.sendto(make_packet(PacketId.MOTION), receiver.address)
#         packet = receiver.receive()

#     assert packet.packet_id is PacketId.MOTION
#     assert packet.source_address is not None
#     assert packet.source_address[0] == "127.0.0.1"


# def test_team_ids_match_protocol_values() -> None:
#     assert TeamId.MERCEDES.value == 0
#     assert TeamId.F1_GENERIC.value == 41
#     assert TeamId.ART_GP_25.value == 465
#     assert TeamId.MERCEDES_26.value == 476
#     assert TeamId.INVICTA_26.value == 499


# def test_driver_ids_match_protocol_values() -> None:
#     assert DriverId.CARLOS_SAINZ.value == 0
#     assert DriverId.ALEXANDER_ALBON.value == 62
#     assert DriverId.ANDREA_KIMI_ANTONELLI.value == 165
#     assert DriverId.SONNY_HAYES.value == 170
#     assert DriverId.NICO_VARRONE.value == 207


# def test_track_ids_match_protocol_values() -> None:
#     assert TrackId.MELBOURNE.value == 0
#     assert TrackId.SAKHIR.value == 3
#     assert TrackId.BAKU.value == 20
#     assert TrackId.SILVERSTONE_REVERSE.value == 39
#     assert TrackId.MADRID.value == 42


# def test_nationality_ids_match_protocol_values() -> None:
#     assert NationalityId.AMERICAN.value == 1
#     assert NationalityId.GREEK.value == 31
#     assert NationalityId.PARAGUAYAN.value == 61
#     assert NationalityId.SALVADORAN.value == 68
#     assert NationalityId.FILIPINO.value == 90
