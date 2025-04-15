"""
Models and type definitions for cargo items.

This module contains all cargo-related data structures, including models,
type definitions, and validation types.
"""
from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.constants import ECargoType


class CargoItem(BaseModel):
    """Cargo item model."""
    id: Optional[str] = None
    cargo_type: ECargoType
    number_of_packages: int = Field(gt=0)
    container_number: Optional[str] = None
    master_bill_of_lading_number: Optional[str] = None
    house_bill_of_lading_number: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
