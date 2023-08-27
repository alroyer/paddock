import struct

from packet.event import button_status_to_buttons
from packet.information import PacketHeader


def main():
    with open('./data/telemetry.bin', 'rb') as file:
        data = file.read()
        print(len(data))

        header = PacketHeader(*struct.unpack('<HBBBBBQfIIBB', data[:29]))
        print(header)

        event_string_code = ''.join([chr(b) for b in struct.unpack('BBBB', data[29:33])])
        print(event_string_code)

        button_status = struct.unpack('I', data[33:37])[0]
        print(button_status)

        buttons = button_status_to_buttons(button_status)
        print(buttons)


if __name__ == '__main__':
    main()
