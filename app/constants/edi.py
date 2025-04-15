from enum import Enum


class EEDISegmentType(str, Enum):
    """Enum for EDI segment types."""

    LIN = "LIN"  # Line item
    PAC = "PAC"  # Package
    PCI = "PCI"  # Package identification
    RFF = "RFF"  # Reference
