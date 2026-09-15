from types import SimpleNamespace
from typing import cast

from telemetry.analyze.ers import _ers_samples, ers_usage
from telemetry.analyze.index import Index


def status_packet(
    time: float,
    store_energy: float,
    deployed: float,
    harvested_mguk: float,
    harvested_mguh: float,
    deploy_mode: int,
):
    return SimpleNamespace(
        header=SimpleNamespace(session_time=time),
        car_status_data=[
            SimpleNamespace(
                ers_store_energy=store_energy,
                ers_deployed_this_lap=deployed,
                ers_harvested_this_lap_mguk=harvested_mguk,
                ers_harvested_this_lap_mguh=harvested_mguh,
                ers_deploy_mode=deploy_mode,
            )
        ],
    )


def index_with(status=None):
    return cast(
        Index,
        SimpleNamespace(
            cars={0: SimpleNamespace(car_status=status or [])},
        ),
    )


def test_ers_samples_extracts_time_and_status_data():
    packets = [status_packet(1.0, 100.0, 1.0, 2.0, 3.0, 1)]

    samples = _ers_samples(index_with(packets), 0)

    assert samples[0][0] == 1.0
    assert samples[0][1].ers_store_energy == 100.0


def test_ers_usage_returns_empty_summary_without_status_samples():
    assert ers_usage(index_with(), 0) == {
        "store_energy_kj": None,
        "deployed_last_lap_kj": None,
        "harvested_last_lap_kj": None,
        "deploy_mode": None,
    }


def test_ers_usage_summarizes_and_rounds_the_last_status_sample():
    index = index_with(
        [
            status_packet(1.0, 10.0, 1.0, 1.0, 1.0, 0),
            status_packet(2.0, 12.345, 6.789, 0.111, 0.222, 2),
        ]
    )

    assert ers_usage(index, 0) == {
        "store_energy_kj": 12.35,
        "deployed_last_lap_kj": 6.79,
        "harvested_last_lap_kj": 0.33,
        "deploy_mode": 2,
    }
