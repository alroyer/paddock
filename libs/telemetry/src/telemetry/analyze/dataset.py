"""TelemetryDataset: facade over an in-memory packet index."""

from pathlib import Path

from ..loader import load_telemetry
from ..packet import BasePacket
from . import driving, ers, fuel, laps as laps_mod, strategy, tyres
from .index import Index, build_index
from .refs import resolve_car
from .session_board import session_board
from .types import CarRef


class TelemetryDataset:
    """Lazily-built read-only view over a session of telemetry packets."""

    def __init__(self, packets: list[BasePacket]) -> None:
        self._index = build_index(packets)

    @classmethod
    def from_file(cls, path: str | Path) -> TelemetryDataset:
        return cls(load_telemetry(path))

    @property
    def index(self) -> Index:
        return self._index

    def cars(self) -> list[dict]:
        """Driver list: name, team, car number, is_player, best_lap_ms."""
        result: list[dict] = []
        for ci in range(self._index.n_cars):
            name = self._name(ci)
            if name is None:
                continue
            best = laps_mod.best_lap_ms(self._index, ci)
            result.append(
                {
                    "car_idx": ci,
                    "name": name,
                    "race_number": self._race_number(ci),
                    "team_id": self._team_id(ci),
                    "is_player": ci == self._index.player_car_index,
                    "best_lap_ms": best,
                }
            )
        return result

    def car(self, ref: CarRef) -> dict:
        ci = resolve_car(self._index, ref)
        info = next((c for c in self.cars() if c["car_idx"] == ci), None)
        if info is None:
            info = {
                "car_idx": ci,
                "name": self._name(ci) or f"car_{ci}",
                "race_number": self._race_number(ci),
                "team_id": self._team_id(ci),
                "is_player": ci == self._index.player_car_index,
                "best_lap_ms": None,
            }
        best_laps = self.best_laps(ci)
        info["best_lap_ms"] = best_laps[0]["lap_time_ms"] if best_laps else None
        return info

    def laps(self, ref: CarRef, limit: int | None = None) -> list[dict]:
        """Validated laps, oldest first (lap 1 = first completed lap)."""
        ci = resolve_car(self._index, ref)
        laps = lap_summaries(self._index, ci)
        return laps[-limit:] if limit else laps

    def best_laps(self, ref: CarRef, limit: int = 3) -> list[dict]:
        ci = resolve_car(self._index, ref)
        laps = [
            lap
            for lap in self.laps(ci)
            if lap["lap_time_ms"] and lap["lap_time_ms"] > 0
        ]
        laps.sort(key=lambda lap: lap["lap_time_ms"])
        return laps[:limit]

    def _name(self, ci: int) -> str | None:
        for packet in self._index.participants:
            if ci < len(packet.participants):
                return packet.participants[ci].name
        return None

    def _race_number(self, ci: int) -> int | None:
        for packet in self._index.participants:
            if ci < len(packet.participants):
                return packet.participants[ci].race_number
        return None

    def _team_id(self, ci: int) -> int | None:
        for packet in self._index.participants:
            if ci < len(packet.participants):
                return packet.participants[ci].team_id
        return None
