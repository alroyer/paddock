#: F1 telemetry tyre compound ids.
TYRE_COMPOUND = {
    0: "SOFT",
    1: "MEDIUM",
    2: "HARD",
    3: "INTERMEDIATE",
    4: "WET",
    5: "UNKNOWN",
}


def tyre_compound_name(compound_id: int) -> str:
    return TYRE_COMPOUND.get(compound_id, "UNKNOWN")


#: F1 telemetry pit status ids (PIT_STATUS in the SDK).
PIT_STATUS = {
    0: "NONE",
    1: "IN",
    2: "OUT",
    3: "SERVED",
    4: "SHOULD_SERVE",
    5: "NOT_SERVED",
}


def pit_status_name(status_id: int) -> str:
    return PIT_STATUS.get(status_id, "UNKNOWN")
