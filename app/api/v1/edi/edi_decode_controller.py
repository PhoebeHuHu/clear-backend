"""EDI decoding controller."""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.constants.error_messages import EErrorMessage
from app.db.cargo_repository import CargoRepository
from app.db.edi_repository import EDIRepository
from app.models.responses import EDIDecodeResponse, ProcessingError
from app.services.cargo_edi.edi_decode import EDIDecodingService

router = APIRouter(tags=["EDI"])


class DecodeEDIRequest(BaseModel):
    """Request model for EDI decoding."""

    edi_content: str


def _convert_errors_to_dict(errors: list[ProcessingError]) -> list[dict[str, Any]]:
    """Convert ProcessingError objects to dictionaries."""
    return [{"message": error.message, "index": error.index} for error in errors]


@router.post("/decode")
async def decode_edi_handler(request: DecodeEDIRequest) -> EDIDecodeResponse:
    """Decode EDI message into cargo items and store in database."""
    # Check for empty content
    if not request.edi_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EErrorMessage.NO_ITEMS)

    # Initialize services
    cargo_repository = CargoRepository()
    edi_repository = EDIRepository()
    edi_service = EDIDecodingService(cargo_repository, edi_repository)

    # Process the EDI message
    cargo_items, errors = await edi_service.decode_edi_message(request.edi_content)

    # Convert errors to dictionary format if they exist
    error_dicts = _convert_errors_to_dict(errors) if errors else None

    # If we have cargo items, return them with any errors (partial success)
    if cargo_items:
        return EDIDecodeResponse(cargo_items=cargo_items, errors=error_dicts)

    # If we have no items but have errors, all segments were invalid
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_dicts)

    # Should never reach here, but just in case
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to decode EDI message")
