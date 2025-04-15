"""Error handling utilities for the application."""
from typing import Any, Optional, Union

from fastapi import HTTPException
from pydantic import ValidationError

from app.constants.error_messages import EErrorMessage
from app.models.cargo_item import CargoItem
from app.models.responses import ProcessingError


def raise_error(message: str, status_code: int = 400) -> None:
    """
    Raise an HTTP error with the given message.

    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
    """
    raise HTTPException(status_code=status_code, detail=message)


def create_error_response(
    error: Optional[str] = None,
    item: Optional[Union[CargoItem, dict]] = None,
    index: Optional[int] = None,
    validation_errors: Optional[list[ProcessingError]] = None
) -> dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        error: Error message
        item: The item that caused the error
        index: Index of the item in a list (if applicable)
        validation_errors: List of validation errors

    Returns:
        Standardized error response dictionary
    """
    if isinstance(item, CargoItem):
        idx = getattr(item, 'index', None)
        item_data = item
    else:
        idx = index
        item_data = item

    response = {
        "index": idx if idx is not None else -1,
        "error": str(error or EErrorMessage.UNKNOWN_ERROR),
        "item": item_data
    }

    if validation_errors:
        response["validation_errors"] = validation_errors

    return response


def handle_validation_error(e: ValidationError, item: dict, index: int) -> dict[str, Any]:
    """
    Handle Pydantic validation errors.

    Args:
        e: The validation error
        item: The item that caused the error
        index: Index of the item

    Returns:
        Error response dictionary
    """
    return create_error_response(
        error=str(e),
        item=item,
        index=index
    )
