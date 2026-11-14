from types import SimpleNamespace

from paddock_cli import main
from typer.testing import CliRunner

runner = CliRunner()


def test_record_data_command_records_and_reports_summary(monkeypatch, tmp_path) -> None:
    class FakeRecorder:
        def __init__(self, host: str, port: int, data_dir) -> None:
            self.host = host
            self.port = port
            self.data_dir = data_dir
            self.output_path = data_dir / "telemetry_fake.bin"
            self.address = ("0.0.0.0", 20777)
            self.stats = SimpleNamespace(packets=42, bytes=1337)

        def start(self):
            return self.output_path

        def run(self) -> None:
            raise KeyboardInterrupt

        def close(self) -> None:
            pass

    monkeypatch.setattr(main, "TelemetryRecorder", FakeRecorder)

    result = runner.invoke(main.app, [], env={"PADDOCK_CLI_DATA_DIR": str(tmp_path)})

    assert result.exit_code == 0
    assert "0.0.0.0:20777" in result.stdout
    assert "telemetry_fake.bin" in result.stdout
    assert "42" in result.stdout
    assert "1337" in result.stdout


def test_record_data_command_reports_bind_failure(monkeypatch, tmp_path) -> None:
    class BrokenRecorder:
        def __init__(self, host: str, port: int, data_dir) -> None:
            pass

        def start(self):
            raise OSError("[Errno 98] Address already in use")

        def close(self) -> None:
            pass

    monkeypatch.setattr(main, "TelemetryRecorder", BrokenRecorder)

    result = runner.invoke(main.app, [], env={"PADDOCK_CLI_DATA_DIR": str(tmp_path)})

    assert result.exit_code == 1
    assert "Could not bind" in result.stdout
    assert "Address already in use" in result.stdout


def test_record_data_command_uses_env_configuration(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}

    class CapturingRecorder:
        def __init__(self, host: str, port: int, data_dir) -> None:
            captured["host"] = host
            captured["port"] = port
            captured["data_dir"] = data_dir
            self.output_path = data_dir / "telemetry_fake.bin"
            self.address = (host, port)
            self.stats = SimpleNamespace(packets=0, bytes=0)

        def start(self):
            return self.output_path

        def run(self) -> None:
            raise KeyboardInterrupt

        def close(self) -> None:
            pass

    monkeypatch.setattr(main, "TelemetryRecorder", CapturingRecorder)
    env = {
        "PADDOCK_CLI_UDP_HOST": "127.0.0.1",
        "PADDOCK_CLI_UDP_PORT": "40404",
        "PADDOCK_CLI_DATA_DIR": str(tmp_path),
    }

    result = runner.invoke(main.app, [], env=env)

    assert result.exit_code == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 40404
    assert str(captured["data_dir"]) == str(tmp_path)
