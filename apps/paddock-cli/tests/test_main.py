from types import SimpleNamespace

from paddock_cli import main
from typer.testing import CliRunner

runner = CliRunner()


def test_format_lap_time_handles_missing_and_formats_milliseconds():
    assert main._format_lap_time(None) == "—"
    assert main._format_lap_time(93_349) == "1:33.349"


def test_car_reference_defaults_to_player_and_accepts_index_or_name():
    assert main._car_reference(None, 4) == 4
    assert main._car_reference("2", 4) == 2
    assert main._car_reference("PIASTRI", 4) == "PIASTRI"


def test_analyze_uses_player_car_by_default(monkeypatch):
    calls = []

    class Dataset:
        index = SimpleNamespace(player_car_index=3)

        @classmethod
        def from_file(cls, path):
            return cls()

        def car(self, reference):
            calls.append(("car", reference))
            return {"name": "PLAYER", "best_lap_ms": 90_000}

        def laps(self, reference):
            calls.append(("laps", reference))
            return []

        def board(self):
            return []

        def fuel_profile(self, reference):
            return {"consumption_kg_per_lap": None}

        def ers_usage(self, reference):
            return {"store_energy_kj": None}

        def tyre_strategy(self, reference):
            return []

        def pit_stops(self, reference):
            return []

        def tyre_degradation(self, reference):
            return {}

    monkeypatch.setattr(main, "TelemetryDataset", Dataset)

    result = runner.invoke(main.app, ["analyze", "session.bin"])

    assert result.exit_code == 0
    assert calls == [("car", 3), ("laps", 3)]
    assert "PLAYER" in result.stdout


def test_analyze_reports_file_errors(monkeypatch):
    class Dataset:
        @classmethod
        def from_file(cls, path):
            raise OSError("missing file")

    monkeypatch.setattr(main, "TelemetryDataset", Dataset)

    result = runner.invoke(main.app, ["analyze", "missing.bin"])

    assert result.exit_code != 0
    assert "Could not analyze missing.bin: missing file" in result.stdout