import socket

UDP_IP = '0.0.0.0'
UDP_PORT = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

with open('./data/telemetry.bin', 'wb') as file:
    while True:
        data, _ = sock.recvfrom(1024)
        file.write(data)
