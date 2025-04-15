"""Response models for API endpoints."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.cargo_item import CargoItem


class ProcessingError(BaseModel):
    """Error information with index of failed item."""

    message: str
    index: Optional[int] = None  # None means it's a general error

    model_config = ConfigDict(from_attributes=True)


class EDIDecodeResponse(BaseModel):
    """Response model for EDI decode endpoint."""

    cargo_items: list[CargoItem]
    errors: Optional[list[dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)


class EDIGenerateResponse(BaseModel):
    """Response model for EDI generate endpoint."""

    edi_content: str
    errors: Optional[list[dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)
