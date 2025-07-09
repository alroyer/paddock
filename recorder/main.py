import os
import socket
from dataclasses import dataclass
from datetime import datetime

import yaml


@dataclass
class Config:
    directory: str
    host: str
    port: int


def read_config() -> Config:
    with open("config.yaml", "r") as file:
        config_data = yaml.safe_load(file)
        return Config(**config_data)


def make_telemetry_filename() -> str:
    return f"telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"


def start_server(host: str, port: int, directory: str) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    filename = make_telemetry_filename()
    filepath = f"{directory}/{filename}"

    with open(filepath, "wb") as file:
        print(f"Server started on {host}:{port}, saving data to {filepath}")
        while True:
            data, _ = sock.recvfrom(1024)
            file.write(data)
            print(f"Received data: {len(data)} bytes")


def main():
    config = read_config()
    if not os.path.exists(config.directory):
        os.makedirs(config.directory)
    start_server(config.host, config.port, config.directory)


if __name__ == "__main__":
    main()
