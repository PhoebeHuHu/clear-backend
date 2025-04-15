"""Tests for EDI decoding functionality."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.constants.error_messages import EErrorMessage
from app.db.cargo_repository import CargoRepository
from app.db.edi_repository import EDIRepository
from app.services.edi_decode import EDIDecodingService

# Test data
VALID_EDI_MESSAGE = """LIN+1+I'
PAC+++LCL:67:95'
PAC+9+1'
PCI+1'
RFF+AAQ:ABC123'
PCI+1'
RFF+MB:DEF456'
PCI+1'
RFF+BH:GHI789'"""

VALID_EDI_MESSAGE_MULTIPLE = """LIN+1+I'
PAC+++LCL:67:95'
PAC+9+1'
PCI+1'
RFF+AAQ:ABC123'
PCI+1'
RFF+MB:DEF456'
PCI+1'
RFF+BH:GHI789'
LIN+2+I'
PAC+++FCL:67:95'
PAC+3+1'
PCI+1'
RFF+AAQ:BETA123'
PCI+1'
RFF+MB:GAMMA345'"""

INVALID_EDI_MESSAGE = """LIN+1+I'
INVALID_SEGMENT+++LCL:67:95'
PAC+INVALID+1'"""

MIXED_EDI_MESSAGE = """LIN+1+I'
PAC+++LCL:67:95'
PAC+9+1'
PCI+1'
RFF+AAQ:ABC123'
PCI+1'
RFF+MB:DEF456'
LIN+2+I'
PAC+++INVALID_TYPE:67:95'
PAC+NOT_A_NUMBER+1'
PCI+1'
RFF+INVALID:XYZ'
LIN+3+I'
PAC+++FCL:67:95'
PAC+5+1'
PCI+1'
RFF+AAQ:GHI789'
PCI+1'
RFF+MB:JKL012'"""

EMPTY_EDI_MESSAGE = ""


@pytest.fixture
def edi_service() -> EDIDecodingService:
    """Fixture for EDI decoding service."""
    return EDIDecodingService(cargo_repository=CargoRepository(), edi_repository=EDIRepository())


@pytest.mark.asyncio
async def test_decode_valid_single_message(edi_service: EDIDecodingService) -> None:
    """Test decoding a valid EDI message with single cargo item."""
    cargo_items, errors = await edi_service.decode_edi_message(VALID_EDI_MESSAGE)

    assert len(cargo_items) == 1
    assert not errors

    cargo = cargo_items[0]
    assert cargo.cargo_type == "LCL"
    assert cargo.number_of_packages == 9
    assert cargo.container_number == "ABC123"
    assert cargo.master_bill_of_lading_number == "DEF456"
    assert cargo.house_bill_of_lading_number == "GHI789"


@pytest.mark.asyncio
async def test_decode_valid_multiple_messages(edi_service: EDIDecodingService) -> None:
    """Test decoding a valid EDI message with multiple cargo items."""
    cargo_items, errors = await edi_service.decode_edi_message(VALID_EDI_MESSAGE_MULTIPLE)

    assert len(cargo_items) == 2
    assert not errors

    # Check first cargo item
    cargo1 = cargo_items[0]
    assert cargo1.cargo_type == "LCL"
    assert cargo1.number_of_packages == 9
    assert cargo1.container_number == "ABC123"
    assert cargo1.master_bill_of_lading_number == "DEF456"
    assert cargo1.house_bill_of_lading_number == "GHI789"

    # Check second cargo item
    cargo2 = cargo_items[1]
    assert cargo2.cargo_type == "FCL"
    assert cargo2.number_of_packages == 3
    assert cargo2.container_number == "BETA123"
    assert cargo2.master_bill_of_lading_number == "GAMMA345"
    assert cargo2.house_bill_of_lading_number is None


@pytest.mark.asyncio
async def test_decode_mixed_valid_invalid_messages(edi_service: EDIDecodingService) -> None:
    """Test decoding a message containing both valid and invalid cargo items."""
    cargo_items, errors = await edi_service.decode_edi_message(MIXED_EDI_MESSAGE)

    # Should have 2 valid cargo items (first and third)
    assert len(cargo_items) == 2

    # Check first valid cargo item
    cargo1 = cargo_items[0]
    assert cargo1.cargo_type == "LCL"
    assert cargo1.number_of_packages == 9
    assert cargo1.container_number == "ABC123"
    assert cargo1.master_bill_of_lading_number == "DEF456"

    # Check second valid cargo item
    cargo2 = cargo_items[1]
    assert cargo2.cargo_type == "FCL"
    assert cargo2.number_of_packages == 5
    assert cargo2.container_number == "GHI789"
    assert cargo2.master_bill_of_lading_number == "JKL012"

    # Should have errors for the invalid cargo
    assert len(errors) > 0
    invalid_cargo_errors = [e for e in errors if e.index is not None]
    assert len(invalid_cargo_errors) > 0

    # Verify error details for invalid cargo
    error = invalid_cargo_errors[0]
    assert error.index == 1  # Second cargo item (0-based index)
    assert any(EErrorMessage.INVALID_CARGO_TYPE_FORMAT.format("INVALID_TYPE") in error.message for error in errors)
    assert any(EErrorMessage.INVALID_NUMBER_FORMAT.format("NOT_A_NUMBER") in error.message for error in errors)
    assert any(EErrorMessage.INVALID_REFERENCE_FORMAT.format("INVALID:XYZ") in error.message for error in errors)


@pytest.mark.asyncio
async def test_decode_mixed_message_endpoint(client: TestClient) -> None:
    """Test the decode endpoint with a mixed valid/invalid message."""
    response = await client.post("/api/v1/edi/decode", json={"edi_content": MIXED_EDI_MESSAGE})

    assert response.status_code == 200
    data = response.json()

    # Should have 2 valid cargo items
    assert len(data["cargo_items"]) == 2

    # Should have errors for the invalid cargo
    assert data["errors"] is not None
    assert len(data["errors"]) > 0

    # Verify valid cargo items are correctly decoded
    cargo_items = data["cargo_items"]

    # Check first cargo item
    assert cargo_items[0]["cargo_type"] == "LCL"
    assert cargo_items[0]["number_of_packages"] == 9
    assert cargo_items[0]["container_number"] == "ABC123"
    assert cargo_items[0]["master_bill_of_lading_number"] == "DEF456"

    # Check second cargo item
    assert cargo_items[1]["cargo_type"] == "FCL"
    assert cargo_items[1]["number_of_packages"] == 5
    assert cargo_items[1]["container_number"] == "GHI789"
    assert cargo_items[1]["master_bill_of_lading_number"] == "JKL012"

    # Verify errors contain necessary information and use correct error messages
    errors = data["errors"]
    error_messages = [error["message"] for error in errors]
    assert any(EErrorMessage.INVALID_CARGO_TYPE_FORMAT.format("INVALID_TYPE") in msg for msg in error_messages)
    assert any(EErrorMessage.INVALID_NUMBER_FORMAT.format("NOT_A_NUMBER") in msg for msg in error_messages)
    assert any(EErrorMessage.INVALID_REFERENCE_FORMAT.format("INVALID:XYZ") in msg for msg in error_messages)


@pytest.mark.asyncio
async def test_decode_invalid_message(edi_service):
    """Test decoding an invalid EDI message."""
    cargo_items, errors = await edi_service.decode_edi_message(INVALID_EDI_MESSAGE)

    assert len(cargo_items) == 0
    assert len(errors) > 0
    # Verify error details are included and use correct error messages
    error_messages = [error.message for error in errors]
    assert any(EErrorMessage.INVALID_SEGMENT_TYPE.format("INVALID_SEGMENT") in msg for msg in error_messages)
    assert any(EErrorMessage.INVALID_NUMBER_FORMAT.format("INVALID") in msg for msg in error_messages)


@pytest.mark.asyncio
async def test_decode_empty_message(edi_service):
    """Test decoding an empty EDI message."""
    cargo_items, errors = await edi_service.decode_edi_message(EMPTY_EDI_MESSAGE)

    assert len(cargo_items) == 0
    assert len(errors) == 1
    assert errors[0].message == EErrorMessage.NO_ITEMS


@pytest.mark.asyncio
async def test_decode_message_with_special_characters(edi_service):
    """Test decoding an EDI message with special characters."""
    message = """LIN+1+I'
PAC+++LCL:67:95'
PAC+9+1'
RFF+AAQ:ABC?'123'"""  # Note the escaped quote

    cargo_items, errors = await edi_service.decode_edi_message(message)

    assert len(cargo_items) == 1
    assert not errors
    assert cargo_items[0].container_number == "ABC'123"  # Quote should be unescaped


@pytest.mark.asyncio
async def test_decode_partial_message(edi_service):
    """Test decoding a partial EDI message with missing optional fields."""
    message = """LIN+1+I'
PAC+++LCL:67:95'
PAC+9+1'
RFF+AAQ:ABC123'"""  # Missing bill of lading numbers

    cargo_items, errors = await edi_service.decode_edi_message(message)

    assert len(cargo_items) == 1
    assert not errors
    assert cargo_items[0].container_number == "ABC123"
    assert cargo_items[0].master_bill_of_lading_number is None
    assert cargo_items[0].house_bill_of_lading_number is None


# API endpoint tests
@pytest.mark.asyncio
async def test_decode_endpoint_valid_request(client):
    """Test the decode endpoint with a valid request."""
    response = await client.post("/api/v1/edi/decode", json={"edi_content": VALID_EDI_MESSAGE})

    assert response.status_code == 200
    data = response.json()
    assert len(data["cargo_items"]) == 1
    assert data["errors"] is None


@pytest.mark.asyncio
async def test_decode_endpoint_empty_request(client):
    """Test the decode endpoint with an empty request."""
    response = await client.post("/api/v1/edi/decode", json={"edi_content": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == EErrorMessage.NO_ITEMS


@pytest.mark.asyncio
async def test_decode_endpoint_invalid_request(client):
    """Test the decode endpoint with an invalid request."""
    response = await client.post("/api/v1/edi/decode", json={"edi_content": INVALID_EDI_MESSAGE})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert isinstance(data["detail"], list)
    assert len(data["detail"]) > 0

    # Verify error messages use constants
    error_messages = [error["message"] for error in data["detail"]]
    assert any(EErrorMessage.INVALID_SEGMENT_TYPE.format("INVALID_SEGMENT") in msg for msg in error_messages)
    assert any(EErrorMessage.INVALID_NUMBER_FORMAT.format("INVALID") in msg for msg in error_messages)
