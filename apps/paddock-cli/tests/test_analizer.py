from types import SimpleNamespace

from paddock_cli import analizer


class Dataset:
    index = SimpleNamespace(player_car_index=1)

    def car(self, reference):
        assert reference == 1
        return {"car_idx": 1, "name": "PLAYER", "best_lap_ms": 90_000}

    def laps(self, reference):
        assert reference == 1
        return [
            {"lap": 1, "lap_time_ms": 92_000, "invalidated": False},
            {"lap": 2, "lap_time_ms": 90_000, "invalidated": False},
            {"lap": 3, "lap_time_ms": 95_000, "invalidated": True},
        ]

    def sector_breakdown(self, reference, lap):
        assert (reference, lap) == (1, 2)
        return {
            "lap": 2,
            "sectors_ms": [45_000, 45_000],
            "best_sector_ms": [44_000, 43_000],
        }

    def board(self):
        return [
            {"car_idx": 1, "best_lap_ms": 90_000},
            {"car_idx": 2, "name": "RIVAL", "best_lap_ms": 89_500},
        ]

    def fuel_profile(self, reference):
        return {"consumption_kg_per_lap": 1.2}

    def ers_usage(self, reference):
        return {"store_energy_kj": 2.0}

    def tyre_strategy(self, reference):
        return [{"compound": 16}]

    def tyre_degradation(self, reference):
        return {16: [{"lap_time_ms": 90_000}]}

    def gear_usage(self, reference):
        return [{"gear": 6, "share": 0.5}]

    def pit_stops(self, reference):
        return []


def test_analysis_snapshot_contains_coaching_facts():
    analyzer = analizer.TelemetryAnalyzer.__new__(analizer.TelemetryAnalyzer)
    analyzer._dataset = Dataset()

    snapshot = analyzer._analysis_snapshot()

    assert snapshot["best_lap"]["lap"] == 2
    assert snapshot["average_lap_ms"] == 91_000
    assert snapshot["consistency_stddev_ms"] == 1_000
    assert snapshot["invalidated_laps"] == 1
    assert snapshot["sector_breakdown_best_lap"]["best_sector_ms"] == [44_000, 43_000]
    assert snapshot["best_rival"]["name"] == "RIVAL"


def test_analyze_can_replace_the_dataset(monkeypatch):
    agents = []

    class FakeAgent:
        def __init__(self, **kwargs):
            agents.append(self)

        async def run(self, prompt):
            self.prompt = prompt
            return SimpleNamespace(output="Conseils")

    monkeypatch.setattr(analizer, "Agent", FakeAgent)
    first = Dataset()
    second = Dataset()
    analyzer = analizer.TelemetryAnalyzer(first, model=object())

    assert analyzer.analyze(second) == "Conseils"
    assert analyzer._dataset is second
    assert "Call the telemetry analysis tool first" in agents[0].prompt
