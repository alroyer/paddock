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


def main():
    config = read_config()
    print(f"Configuration loaded: {config}")


if __name__ == "__main__":
    main()
