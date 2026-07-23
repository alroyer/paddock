from telemetry.filters import filter_packets, list_sessions
from telemetry.loader import load_telemetry
from telemetry.packet import PacketId


def main():
    packets = load_telemetry("./data/telemetry_data_2026-07-21_10-22-44.bin")
    print(f"Loaded {len(packets)} packets")

    sessions = filter_packets(packets, packet_id=PacketId.Session)
    print(f"Found {len(sessions)} sessions")


if __name__ == "__main__":
    main()
