import asyncio
import statistics
from typing import Any

from pydantic_ai.agent import Agent
from pydantic_ai.models.ollama import OllamaModel
from telemetry.analyze import TelemetryDataset


class TelemetryAnalyzer:
    def __init__(self, dataset: TelemetryDataset, model: OllamaModel):
        self._dataset = dataset

        def _analyze() -> dict[str, Any]:
            """Return the telemetry facts Hannah must use for her advice."""
            return self._analysis_snapshot()

        self._agent = Agent(
            model=model,
            description=(
                "You are Hannah, a F1 telemetry coach. Help the driver improve lap times "
                "with precise, actionable advice grounded only in the telemetry tool. "
                "Your analysis should focus on what data is actually available and avoid "
                "making assumptions about driving techniques that aren't directly observable. "
                "Be honest about your limitations - you cannot identify specific dangerous "
                "driving patterns like excessive corner speeds or improper cornering because "
                "the telemetry doesn't provide that level of detail. Focus on what you can "
                "observe: speed trends, gear usage, brake/throttle application, lap time "
                "performance, and sector timing. When analyzing sector performance, "
                "highlight where the driver loses time compared to their best lap or the track record."
            ),
            output_type=str,
            tools=[_analyze],
        )

    def analyze(self, telemetry_dataset: TelemetryDataset | None = None) -> str:
        if telemetry_dataset is not None:
            self._dataset = telemetry_dataset

        prompt = (
            "Call the telemetry analysis tool first. Then answer in French with a "
            "short coaching report: identify the biggest time loss opportunities, "
            "quantify them when possible, and give three concrete priorities for the next laps. "
            "Do not invent telemetry values or driving problems. Focus on what is actually measurable "
            "in the data - avoid making claims about dangerous driving patterns that aren't supported "
            "by the available telemetry. Be honest about your limitations. "
            "Highlight sectors where time is lost compared to best performance and suggest "
            "how to improve those specific areas based on the available data."
        )
        response = asyncio.run(self._agent.run(prompt))
        return response.output

    def _analysis_snapshot(self) -> dict[str, Any]:
        dataset = self._dataset
        reference = dataset.index.player_car_index
        driver = dataset.car(reference)
        laps = dataset.laps(reference)
        valid_laps = [
            lap
            for lap in laps
            if lap.get("lap_time_ms", 0) > 0 and not lap.get("invalidated", False)
        ]
        best_lap = (
            min(valid_laps, key=lambda lap: lap["lap_time_ms"]) if valid_laps else None
        )

        sector_breakdown = None
        if best_lap is not None:
            sector_breakdown = dataset.sector_breakdown(reference, best_lap["lap"])

        lap_times = [lap["lap_time_ms"] for lap in valid_laps]
        rivals = [
            row
            for row in dataset.board()
            if row.get("car_idx") != driver["car_idx"] and row.get("best_lap_ms")
        ]

        return {
            "driver": driver,
            "completed_laps": len(laps),
            "valid_laps": len(valid_laps),
            "best_lap": best_lap,
            "average_lap_ms": round(statistics.mean(lap_times)) if lap_times else None,
            "consistency_stddev_ms": round(statistics.pstdev(lap_times), 1)
            if len(lap_times) > 1
            else None,
            "invalidated_laps": sum(1 for lap in laps if lap.get("invalidated", False)),
            "sector_breakdown_best_lap": sector_breakdown,
            "best_rival": min(rivals, key=lambda row: row["best_lap_ms"])
            if rivals
            else None,
            "fuel": dataset.fuel_profile(reference),
            "ers": dataset.ers_usage(reference),
            "tyre_stints": dataset.tyre_strategy(reference),
            "tyre_degradation": dataset.tyre_degradation(reference),
            "gear_usage": dataset.gear_usage(reference),
            "pit_stops": dataset.pit_stops(reference),
        }
