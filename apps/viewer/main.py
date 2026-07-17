from telemetry.filters import list_packets, list_sessions
from telemetry.loader import load_telemetry


def main():
    packets = load_telemetry("./data/telemetry_data_2026-07-11_14-26-57.bin")
    print(f"Loaded {len(packets)} packets")

    sessions = list_sessions(packets)
    print(f"Found sessions: {sessions}")

    for session in sessions:
        session_packets = list_packets(session, packets)
        print(f"Session {session} has {len(session_packets)} packets")


if __name__ == "__main__":
    main()
