"""Validation utilities for the application."""
import re
from collections.abc import Sequence
from typing import Any

from app.constants.validation import VALID_ASCII_PATTERN
from app.models.responses import ProcessingError


def validate_ascii_characters(
    data: dict[str, Any] | str | None,
    fields: str | Sequence[str] | None = None
) -> list[ProcessingError]:
    """
    Validate that string(s) contain only ASCII characters.

    Args:
        data: Either a dictionary containing fields to validate, or a single string to validate
        fields: Either a single field name or a list of field names to validate (if data is a dict)

    Returns:
        A list of validation errors if any strings contain non-ASCII characters
    """
    errors: list[ProcessingError] = []

    if isinstance(data, dict):
        # If data is a dictionary, validate specified fields
        if fields:  # Only validate specified fields if provided
            field_list = [fields] if isinstance(fields, str) else fields
            for field in field_list:
                if field in data:
                    value = data.get(field)
                    if value and not re.match(VALID_ASCII_PATTERN, value):
                        errors.append(ProcessingError(
                            message=f"{field} contains non-ASCII characters"
                        ))
    elif data:  # If data is a string (and not None)
        # If data is a single string, validate it directly
        field_name = fields if isinstance(fields, str) else "value"
        if not re.match(VALID_ASCII_PATTERN, data):
            errors.append(ProcessingError(
                message=f"{field_name} contains non-ASCII characters"
            ))

    return errors
