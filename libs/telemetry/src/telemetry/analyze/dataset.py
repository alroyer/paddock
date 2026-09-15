"""TelemetryDataset: facade over an in-memory packet index."""

from pathlib import Path

from ..loader import load_telemetry
from ..packet import BasePacket
from . import driving, ers, fuel, strategy, tyres
from . import laps as laps_mod
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
        laps = laps_mod.lap_summaries(self._index, ci)
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

    def board(self) -> list[dict]:
        """Session board: final classification, or last-known positions."""
        return session_board(self._index)

    def sector_breakdown(self, ref: CarRef, lap: int) -> dict:
        """Sectors of one lap against the session best per sector."""
        ci = resolve_car(self._index, ref)
        return laps_mod.sector_breakdown(self._index, ci, lap)

    def compare_laps(self, ref: CarRef, lap_a: int, lap_b: int) -> dict:
        """Lap A vs lap B: time and per-sector differences."""
        ci = resolve_car(self._index, ref)
        return laps_mod.compare_laps(self._index, ci, lap_a, lap_b)

    def speed_trace(self, ref: CarRef, max_points: int = 240) -> list:
        """Downsampled (t, speed_kmh) points for the whole session."""
        ci = resolve_car(self._index, ref)
        return driving.speed_trace(self._index, ci, max_points)

    def gear_usage(self, ref: CarRef) -> list:
        """Gear usage histogram: [{gear, samples, share}, ...]."""
        ci = resolve_car(self._index, ref)
        return driving.gear_usage(self._index, ci)

    def fuel_profile(self, ref: CarRef, max_points: int = 240) -> dict:
        """Fuel load over time + derived consumption stats."""
        ci = resolve_car(self._index, ref)
        return fuel.fuel_profile(self._index, ci, max_points)

    def ers_usage(self, ref: CarRef) -> dict:
        """ERS store level and last-lap harvest/deploy totals."""
        ci = resolve_car(self._index, ref)
        return ers.ers_usage(self._index, ci)

    def tyre_strategy(self, ref: CarRef) -> list[dict]:
        """Tyre stints of the session, in order."""
        ci = resolve_car(self._index, ref)
        return tyres.tyre_strategy(self._index, ci)

    def tyre_degradation(self, ref: CarRef) -> dict:
        """Lap time vs tyre age, grouped by compound."""
        ci = resolve_car(self._index, ref)
        return tyres.tyre_degradation(self._index, ci)

    def pit_stops(self, ref: CarRef) -> list[dict]:
        """Pit stops of the session, in lap order."""
        ci = resolve_car(self._index, ref)
        return strategy.pit_stops(self._index, ci)

    def position_changes(self, ref: CarRef) -> list[dict]:
        """Laps where the car changed position, with the delta."""
        ci = resolve_car(self._index, ref)
        return strategy.position_changes(self._index, ci)

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
