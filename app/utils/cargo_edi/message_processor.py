"""EDI message processing utilities."""

from typing import Any, Optional

from app.constants.error_messages import EErrorMessage
from app.models.cargo_item import CargoItem
from app.models.responses import ProcessingError
from app.utils.cargo_edi.edi_parser import parse_pac_segment, parse_rff_segment, parse_segment, process_edi_content


def process_segment(segment: str, cargo_data: dict[str, Any]) -> list[str]:
    """Process a single EDI segment and update cargo data."""
    errors = []
    try:
        segment_id, elements = parse_segment(segment)

        if segment_id == "PAC":
            segment_data = parse_pac_segment(elements)
            if segment_data:
                cargo_data.update(segment_data)
        elif segment_id == "RFF":
            segment_data = parse_rff_segment(elements)
            if segment_data:
                cargo_data.update(segment_data)

    except ValueError as e:
        errors.append(str(e))

    return errors


def validate_cargo_data(cargo_data: dict[str, Any]) -> list[str]:
    """Validate required fields in cargo data."""
    errors = []
    if "cargo_type" not in cargo_data:
        errors.append(EErrorMessage.MISSING_REQUIRED_FIELD.format("cargo_type"))
    if "number_of_packages" not in cargo_data:
        errors.append(EErrorMessage.MISSING_REQUIRED_FIELD.format("number_of_packages"))
    return errors


def parse_message_group(
    message_group: list[str], group_idx: int
) -> tuple[Optional[CargoItem], Optional[ProcessingError]]:
    """Parse a single message group into a cargo item."""
    cargo_data: dict[str, Any] = {}
    group_errors = []

    # Process each segment in the group
    for segment in message_group:
        segment_errors = process_segment(segment, cargo_data)
        group_errors.extend(segment_errors)

    # Validate required fields
    if not group_errors:
        group_errors.extend(validate_cargo_data(cargo_data))

    # Return results
    if not group_errors and "cargo_type" in cargo_data and "number_of_packages" in cargo_data:
        try:
            cargo_item = CargoItem(**cargo_data)
            return cargo_item, None
        except Exception as e:
            return None, ProcessingError(index=group_idx, message=str(e))

    if group_errors:
        return None, ProcessingError(index=group_idx, message="\n".join(group_errors))

    return None, None


def parse_edi_message(edi_content: str) -> tuple[list[CargoItem], list[ProcessingError]]:
    """Parse EDI message into cargo items.

    Args:
        edi_content: The EDI message to parse

    Returns:
        Tuple containing:
        - List of parsed cargo items
        - List of any errors encountered during parsing
    """
    if not edi_content:
        return [], [ProcessingError(message=EErrorMessage.NO_ITEMS.value)]

    try:
        # Split EDI content into message groups
        message_groups = process_edi_content(edi_content)

        cargo_items = []
        errors = []

        # Parse each message group
        for idx, group in enumerate(message_groups):
            cargo_item, error = parse_message_group(group, idx)
            if cargo_item:
                cargo_items.append(cargo_item)
            if error:
                errors.append(error)

        if not cargo_items and not errors:
            return [], [ProcessingError(message=EErrorMessage.NO_ITEMS.value)]

        return cargo_items, errors

    except Exception as e:
        return [], [ProcessingError(message=f"{EErrorMessage.PROCESSING_ERROR}: {str(e)}")]
