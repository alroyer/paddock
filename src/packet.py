import struct

import packet.constants as constants
from packet.information import PacketHeader


def main():
    with open('./data/telemetry.bin', 'rb') as file:
        data = file.read()
        print(len(data))

        header = PacketHeader(*struct.unpack('<HBBBBBQfIIBB', data[:29]))
        print(header)

        event_string_code = ''.join(
            [chr(b) for b in struct.unpack('BBBB', data[29:33])]
        )
        print(event_string_code)

        button_status = struct.unpack('I', data[33:37])[0]
        print(button_status)

        for bit_flag, button in constants.BUTTON_FLAGS.items():
            if bit_flag & button_status:
                print(button)


if __name__ == '__main__':
    main()
