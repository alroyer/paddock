import logging

from packet.parser import parse

logging.basicConfig(
    filename='logs/main.log',
    filemode='w',
    format='[%(asctime)s] %(levelname)s %(name)s\n\t%(message)s',
    level=logging.INFO,
)


def main():
    with open('./data/telemetry.bin', 'rb') as file:
        data = file.read()

    packets = parse(data)
    for packet in packets:
        print(packet)


if __name__ == '__main__':
    main()
