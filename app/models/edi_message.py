"""EDI message model."""

from datetime import UTC, datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class EDIMessage(BaseModel):
    """EDI message data."""

    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    edi_content: str
    cargo_item_ids: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        """Pydantic model configuration."""

        json_encoders: dict = {ObjectId: str}
        schema_extra: dict = {"example": {"edi_content": "LIN+1+I'\nPAC+++FCL:67:95'\nPAC+10+1'", "cargo_item_ids": []}}
