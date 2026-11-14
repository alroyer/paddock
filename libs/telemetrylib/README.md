# telemetrylib

Python data structures for F1 26 UDP telemetry data.

This library provides Python classes that mirror the C++ telemetry structures
used in F1 26 games for UDP communication. It's designed to be used with the F1 26 UDP protocol to parse and work with telemetry data sent by the game.

## Installation

```bash
uv pip install .
```

## Usage

```python
from telemetrylib import (
    PacketHeader,
    PacketSessionData,
    PacketLapData,
    PacketCarTelemetryData,
)

# Create a session data packet
session_data = PacketSessionData(
    header=PacketHeader(
        packet_format=2026,
        game_year=26,
        game_major_version=1,
        game_minor_version=0,
        packet_version=1,
        packet_id=1,  # ePacketIdSession
        session_uid=123456789,
        session_time=0.0,
        frame_identifier=0,
        overall_frame_identifier=0,
        player_car_index=0,
        secondary_player_car_index=255,
    ),
    # ... initialize other fields as needed
)
```

## Reading UDP telemetry

`decode_packet` decodes one complete F1 26 datagram. `TelemetryReceiver` binds a
UDP socket to port `20777` by default and decodes each received datagram:

```python
from telemetrylib import PacketId, TelemetryReceiver

with TelemetryReceiver() as receiver:
    packet = receiver.receive()
    if packet.packet_id is PacketId.CAR_TELEMETRY:
        cars = packet.payload["car_telemetry_data"]
        player_car = cars[packet.header.player_car_index]
        print(player_car["speed"], player_car["gear"])
```

The decoder supports all packet IDs in the F1 26 format. Payloads are mappings
with `snake_case` keys; fixed-capacity arrays retain their protocol capacity,
and count fields indicate how many entries are active. Invalid, truncated, or
unsupported-format datagrams raise a `TelemetryPacketError` subclass. Socket
timeouts and socket errors are propagated to the caller.

## Structure Overview

This library provides Python dataclasses that mirror the C++ structures in the F1 26 UDP protocol:

- Packet headers and basic telemetry structures
- Session data including weather, track information, and safety car status
- Lap data with timing and position information
- Event data for race events like fastest laps, retirements, penalties
- Participant data including driver information and team details
- Car setup data for aerodynamics and suspension settings
- Car telemetry data including speed, RPM, brake pressure, etc.
- Car status data including damage, fuel, and DRS status
- Final classification and lobby information
- Car damage data
- Session history and tyre set information
- Extended motion data and time trial information

## Constants

- `PacketId`: Enum of all packet types in the F1 26 UDP protocol
- `DriverId`: Enum mapping protocol driver IDs to driver names
- `NationalityId`: Enum mapping protocol nationality IDs to nationality names
- `TeamId`: Enum mapping protocol team IDs to team names and seasons
- `TrackId`: Enum mapping protocol track IDs to circuit names
- `EVENT_CODES`: Dictionary mapping event names to their 4-character codes

## License

MIT