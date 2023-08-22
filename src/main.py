import struct

import packet

with open('./data/telemetry.bin', 'rb') as file:
    data = file.readline()

    header = packet.Header(*struct.unpack('<HBBBBBQfIIBB', data[:29]))
    print(header)
