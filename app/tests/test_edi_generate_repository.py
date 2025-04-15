"""Tests for EDI generation repository storage functionality."""
from datetime import datetime

import pytest
from bson import ObjectId

from app.constants.cargo import ECargoType
from app.db.database import get_database
from app.db.edi_repository import EDIRepository
from app.models.cargo_item import CargoItem

# Test data
SAMPLE_CARGO_ITEMS = [
    CargoItem(
        cargo_type=ECargoType.FCL,
        number_of_packages=10,
        container_number="CONT123456",
        master_bill_of_lading_number="MBL123456",
        house_bill_of_lading_number="HBL123456"
    ),
    CargoItem(
        cargo_type=ECargoType.LCL,
        number_of_packages=5,
        container_number="CONT789012",
        master_bill_of_lading_number="MBL789012"
    )
]

SAMPLE_EDI_CONTENT = """LIN+1+I'
PAC+++FCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:CONT123456'
PCI+1'
RFF+MB:MBL123456'
PCI+1'
RFF+BH:HBL123456'
LIN+2+I'
PAC+++LCL:67:95'
PAC+5+1'
PCI+1'
RFF+AAQ:CONT789012'
PCI+1'
RFF+MB:MBL789012'"""

@pytest.fixture
def edi_repository():
    """Fixture for EDI repository."""
    return EDIRepository()

@pytest.fixture
def sample_cargo_ids():
    """Fixture for sample cargo IDs."""
    return [str(ObjectId()) for _ in range(len(SAMPLE_CARGO_ITEMS))]

@pytest.mark.asyncio
async def test_store_generated_edi_success(edi_repository, sample_cargo_ids):
    """Test successful storage of generated EDI message."""
    result = await EDIRepository.store_edi_message(SAMPLE_EDI_CONTENT, sample_cargo_ids)
    assert result is True

@pytest.mark.asyncio
async def test_store_generated_edi_verify_content(edi_repository, sample_cargo_ids):
    """Test that stored generated EDI message contains all required fields."""
    await EDIRepository.store_edi_message(SAMPLE_EDI_CONTENT, sample_cargo_ids)

    # Verify stored document
    db = get_database()
    stored_doc = await db.edi_messages.find_one({"edi_content": SAMPLE_EDI_CONTENT})

    assert stored_doc is not None
    assert stored_doc["edi_content"] == SAMPLE_EDI_CONTENT
    assert len(stored_doc["cargo_item_ids"]) == len(sample_cargo_ids)
    # Check that all IDs are valid ObjectId strings
    for id_ in stored_doc["cargo_item_ids"]:
        assert isinstance(id_, str)
        assert ObjectId.is_valid(id_)
    assert "created_at" in stored_doc
    assert isinstance(stored_doc["created_at"], datetime)

@pytest.mark.asyncio
async def test_store_generated_edi_with_quotes(edi_repository, sample_cargo_ids):
    """Test storing EDI message with escaped quotes."""
    edi_content = """LIN+1+I'
PAC+++FCL:67:95'
PAC+10+1'
RFF+AAQ:CONT?'123'"""

    result = await EDIRepository.store_edi_message(edi_content, sample_cargo_ids)
    assert result is True

    # Verify stored content
    db = get_database()
    stored_doc = await db.edi_messages.find_one({"edi_content": edi_content})
    assert stored_doc is not None
    assert stored_doc["edi_content"] == edi_content  # Quotes should remain escaped

@pytest.mark.asyncio
async def test_store_generated_edi_empty_cargo_ids(edi_repository):
    """Test storing generated EDI message with no cargo items."""
    edi_content = """LIN+1+I'
PAC+++FCL:67:95'
PAC+10+1'"""

    result = await EDIRepository.store_edi_message(edi_content, [])
    assert result is True

    # Verify stored document has empty cargo_item_ids
    db = get_database()
    stored_doc = await db.edi_messages.find_one({"edi_content": edi_content})
    assert stored_doc is not None
    assert len(stored_doc["cargo_item_ids"]) == 0
