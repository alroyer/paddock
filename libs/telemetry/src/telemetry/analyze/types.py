#: A car can be referenced by its ``car_idx`` (0-21) or by driver name.
type CarRef = int | str


class UnknownCar(ValueError):
    """Raised when a car reference cannot be resolved to a ``car_idx``."""


class UnknownLap(ValueError):
    """Raised when a requested lap does not exist for a car."""
