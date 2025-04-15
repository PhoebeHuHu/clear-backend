"""Tests for EDI repository storage functionality."""

from datetime import datetime

import pytest
from bson import ObjectId

from app.constants.error_messages import EErrorMessage
from app.db.edi_repository import EDIRepository

# Test data
SAMPLE_EDI_CONTENT = """LIN+1+I'
PAC+++LCL:67:95'
PAC+9+1'
RFF+AAQ:ABC123'"""


@pytest.fixture
def edi_repository():
    """Fixture for EDI repository."""
    return EDIRepository()


@pytest.fixture
def sample_cargo_ids():
    """Fixture for sample cargo IDs."""
    return [str(ObjectId()) for _ in range(2)]


@pytest.mark.asyncio
async def test_store_edi_message_success(edi_repository, sample_cargo_ids):
    """Test successful storage of EDI message."""
    result = await EDIRepository.store_edi_message(SAMPLE_EDI_CONTENT, sample_cargo_ids)
    assert result is True


@pytest.mark.asyncio
async def test_store_edi_message_empty_content(edi_repository, sample_cargo_ids):
    """Test storing EDI message with empty content."""
    with pytest.raises(ValueError) as exc_info:
        await EDIRepository.store_edi_message("", sample_cargo_ids)
    assert str(exc_info.value) == EErrorMessage.EMPTY_EDI_CONTENT.value


@pytest.mark.asyncio
async def test_store_edi_message_empty_cargo_ids(edi_repository):
    """Test storing EDI message with empty cargo IDs list."""
    result = await EDIRepository.store_edi_message(SAMPLE_EDI_CONTENT, [])
    assert result is True  # Should still store even with empty cargo IDs


@pytest.mark.asyncio
async def test_store_edi_message_verify_content(edi_repository, sample_cargo_ids):
    """Test that stored EDI message contains all required fields."""
    from app.db.database import get_database

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
