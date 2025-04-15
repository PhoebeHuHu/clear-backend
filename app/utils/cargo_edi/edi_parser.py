"""EDI parsing utilities."""
from typing import Optional

from app.constants.cargo import ECargoType
from app.constants.edi import EEDISegmentType
from app.constants.error_messages import EErrorMessage
from app.utils.cargo_edi.edi_generator import unescape_quotes


def parse_segment(segment: str) -> tuple[str, list[str]]:
    """Parse a segment into its ID and data elements."""
    parts = segment.split('+')
    if len(parts) < 2 or (parts[0] not in ['LIN', 'PCI'] and parts[0] not in [e.value for e in EEDISegmentType]):
        raise ValueError(EErrorMessage.INVALID_SEGMENT_TYPE.format(parts[0]))
    return parts[0], [e.rstrip("'") for e in parts[1:]]


def parse_pac_segment(elements: list[str]) -> dict[str, Optional[str | int]]:
    """Parse PAC segment data."""
    result = {}
    if len(elements) >= 3 and elements[2]:
        cargo_type = elements[2].split(':')[0]
        if cargo_type in [e.value for e in ECargoType]:
            result['cargo_type'] = cargo_type
        else:
            raise ValueError(EErrorMessage.INVALID_CARGO_TYPE_FORMAT.format(cargo_type))

    if elements:
        try:
            package_count = int(elements[0])
            if package_count > 0:
                result['number_of_packages'] = package_count
            else:
                raise ValueError(EErrorMessage.INVALID_PACKAGE_COUNT)
        except ValueError as err:
            raise ValueError(EErrorMessage.INVALID_NUMBER_FORMAT.format(elements[0])) from err
    return result


def parse_rff_segment(elements: list[str]) -> dict[str, str]:
    """Parse RFF segment data."""
    if not elements:
        raise ValueError(EErrorMessage.INVALID_REFERENCE_FORMAT.format(""))

    parts = elements[0].split(':')
    if len(parts) != 2:
        raise ValueError(EErrorMessage.INVALID_REFERENCE_FORMAT.format(elements[0]))

    ref_type, value = parts
    mapping = {'AAQ': 'container_number', 'MB': 'master_bill_of_lading_number', 'BH': 'house_bill_of_lading_number'}

    if ref_type not in mapping or not value:
        raise ValueError(EErrorMessage.INVALID_REFERENCE_FORMAT.format(elements[0]))
    return {mapping[ref_type]: unescape_quotes(value)}


def process_edi_content(edi_content: str) -> list[list[str]]:
    """Process EDI content into grouped messages."""
    if not edi_content.strip():
        raise ValueError(EErrorMessage.NO_ITEMS)

    segments = [s.strip() for s in edi_content.split("\n") if s.strip()]
    if not segments:
        raise ValueError(EErrorMessage.NO_ITEMS)

    messages, current = [], []
    for segment in segments:
        if segment.startswith("LIN+"):
            if current:
                messages.append(current)
            current = [segment]
        else:
            if not current:
                raise ValueError(EErrorMessage.INVALID_SEGMENT_FORMAT)
            current.append(segment)

    if current:
        messages.append(current)

    return messages
