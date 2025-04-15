"""EDI generation controller."""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict

from app.constants.error_messages import EErrorMessage
from app.models.responses import EDIGenerateResponse
from app.services.edi_generate import EDIGenerationService

router = APIRouter(tags=["EDI"])


class GenerateEDIRequest(BaseModel):
    """Request model for EDI generation."""

    items: list[dict[str, Any]]

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


@router.post("/generate")
async def generate_edi_handler(request: GenerateEDIRequest) -> EDIGenerateResponse:
    """Generate EDI messages from a list of cargo items."""
    # Check for empty request
    if not request.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EErrorMessage.NO_ITEMS.value)

    # Use EDI generation service
    service = EDIGenerationService()
    edi_content, errors = await service.generate_edi_message(request.items)

    # Convert errors to dictionaries if there are any
    error_dicts = [{"index": e.index, "message": e.message} for e in errors] if errors else None

    # If we have EDI content, return it with any errors (partial success)
    if edi_content:
        return EDIGenerateResponse(edi_content=edi_content, errors=error_dicts)

    # If we have no content but have errors, all items were invalid
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_dicts)

    # Should never reach here, but just in case
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate EDI message")
