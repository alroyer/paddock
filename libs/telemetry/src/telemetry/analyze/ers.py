"""ERS (energy recovery) analysis: store level, harvest and deploy per lap."""

from .index import Index


def _ers_samples(index: Index, ci: int) -> list:
    return [
        (pkt.header.session_time, cs)
        for pkt in index.cars[ci].car_status
        for cs in [pkt.car_status_data[ci]]
    ]


def ers_usage(index: Index, ci: int) -> dict:
    """ERS energy summary for a car.

    - ``store_energy_kj``: last store energy sample
    - ``deployed_last_lap_kj`` / ``harvested_last_lap_kj``: final lap totals
    - ``deploy_mode``: last deploy mode
    """
    samples = _ers_samples(index, ci)
    if not samples:
        return {
            "store_energy_kj": None,
            "deployed_last_lap_kj": None,
            "harvested_last_lap_kj": None,
            "deploy_mode": None,
        }

    _, cs = samples[-1]
    return {
        "store_energy_kj": round(cs.ers_store_energy, 2),
        "deployed_last_lap_kj": round(cs.ers_deployed_this_lap, 2),
        "harvested_last_lap_kj": round(
            cs.ers_harvested_this_lap_mguk + cs.ers_harvested_this_lap_mguh, 2
        ),
        "deploy_mode": cs.ers_deploy_mode,
    }
