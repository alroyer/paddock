from telemetry.loader import load_telemetry


def main():
    packets = load_telemetry("./data/telemetry_data_2026-07-11_14-26-57.bin")

    for packet in packets:
        print(packet)


if __name__ == "__main__":
    main()
