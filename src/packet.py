from packet.parser import parse


def main():
    with open('./data/telemetry.bin', 'rb') as file:
        data = file.read()

    packets = parse(data)
    print(packets)


if __name__ == '__main__':
    main()
