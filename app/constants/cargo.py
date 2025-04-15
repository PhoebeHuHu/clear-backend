from enum import Enum


class ECargoType(str, Enum):
    """Enum for cargo types."""
    FCX = "FCX"
    LCL = "LCL"
    FCL = "FCL"
