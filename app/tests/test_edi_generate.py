import pytest

from app.constants.cargo import ECargoType
from app.constants.error_messages import EErrorMessage
from app.models.cargo_item import CargoItem
from app.services.cargo_edi.edi_generate import EDIGenerationService
from app.utils.cargo_edi import escape_quotes, generate_edi_segment

# Test Data
VALID_CARGO_ITEM = {
    "cargo_type": "FCL",
    "number_of_packages": 10,
    "container_number": "CONT123456",
    "master_bill_of_lading_number": "MBL123456",
    "house_bill_of_lading_number": "HBL123456"
}

VALID_CARGO_ITEMS = [
    VALID_CARGO_ITEM,
    {
        "cargo_type": "LCL",
        "number_of_packages": 5,
        "container_number": "CONT789012",
        "master_bill_of_lading_number": "MBL789012",
        "house_bill_of_lading_number": "HBL789012"
    }
]

INVALID_CARGO_ITEM = {
    "cargo_type": "INVALID",
    "number_of_packages": -1,
    "container_number": "CONT123€",  # Non-ASCII character
    "master_bill_of_lading_number": "MBL123"
}

MIXED_CARGO_ITEMS = [
    VALID_CARGO_ITEM,
    INVALID_CARGO_ITEM,
    {
        "cargo_type": "FCX",
        "number_of_packages": 3,
        "container_number": "CONT456789"
    }
]

# Unit Tests
def test_escape_quotes() -> None:
    """Test quote escaping in strings."""
    assert escape_quotes("ABC'123") == "ABC?'123"
    assert escape_quotes("ABC??'123") == "ABC?'123"
    assert escape_quotes("ABC???'123") == "ABC?'123"
    assert escape_quotes("ABC'123'456") == "ABC?'123?'456"

@pytest.mark.parametrize("cargo_type", ["FCL", "LCL", "FCX"])
def test_valid_cargo_types(cargo_type: str) -> None:
    """Test validation of valid cargo types."""
    item = CargoItem(
        cargo_type=cargo_type,
        number_of_packages=1,
        container_number="CONT123",
        master_bill_of_lading_number="MBL123"
    )
    assert isinstance(item.cargo_type, ECargoType)

def test_invalid_cargo_type():
    """Test validation of invalid cargo type."""
    with pytest.raises(ValueError):
        CargoItem(
            cargo_type="INVALID",
            number_of_packages=1,
            container_number="TEST123"
        )

@pytest.mark.parametrize("packages", [-1, 0])
def test_invalid_package_count(packages: int) -> None:
    """Test validation of invalid package counts."""
    with pytest.raises(ValueError):
        CargoItem(
            cargo_type="FCL",
            number_of_packages=packages,
            container_number="CONT123",
            master_bill_of_lading_number="MBL123"
        )

@pytest.mark.asyncio
async def test_generate_edi_segment_valid():
    """Test generating EDI segment with valid cargo item."""
    cargo_item = CargoItem(
        cargo_type=ECargoType.FCL,
        number_of_packages=10,
        container_number="CONT123",
        master_bill_of_lading_number="MBL123",
        house_bill_of_lading_number="HBL123"
    )

    result = generate_edi_segment(cargo_item, 1)
    expected_segments = [
        "LIN+1+I'",
        "PAC+++FCL:67:95'",
        "PAC+10+1'",
        "PCI+1'",
        "RFF+AAQ:CONT123'",
        "PCI+1'",
        "RFF+MB:MBL123'",
        "PCI+1'",
        "RFF+BH:HBL123'"
    ]
    for segment in expected_segments:
        assert segment in result

@pytest.mark.asyncio
async def test_generate_edi_segment_with_quotes():
    """Test generating EDI segment with quotes in values."""
    cargo_item = CargoItem(
        cargo_type=ECargoType.LCL,
        number_of_packages=5,
        container_number="CONT'123",
        master_bill_of_lading_number="MBL'123",
        house_bill_of_lading_number="HBL'123"
    )

    result = generate_edi_segment(cargo_item, 2)
    expected_segments = [
        "LIN+2+I'",
        "PAC+++LCL:67:95'",
        "PAC+5+1'",
        "PCI+1'",
        "RFF+AAQ:CONT?'123'",
        "PCI+1'",
        "RFF+MB:MBL?'123'",
        "PCI+1'",
        "RFF+BH:HBL?'123'"
    ]
    for segment in expected_segments:
        assert segment in result

@pytest.mark.asyncio
async def test_generate_edi_segment_empty_values():
    """Test generating EDI segment with empty values."""
    cargo_item = CargoItem(
        cargo_type=ECargoType.FCX,
        number_of_packages=1
    )

    result = generate_edi_segment(cargo_item)
    expected_segments = [
        "LIN+1+I'",
        "PAC+++FCX:67:95'",
        "PAC+1+1'"
    ]
    for segment in expected_segments:
        assert segment in result

@pytest.mark.asyncio
async def test_generate_edi_segment_optional_fields():
    """Test EDI segment generation with optional fields omitted."""
    cargo_item = CargoItem(
        cargo_type=ECargoType.FCL,
        number_of_packages=10
    )

    result = generate_edi_segment(cargo_item, 1)
    expected_segments = [
        "LIN+1+I'",
        "PAC+++FCL:67:95'",
        "PAC+10+1'"
    ]
    for segment in expected_segments:
        assert segment in result

    assert "RFF+AAQ:" not in result
    assert "RFF+MB:" not in result
    assert "RFF+BH:" not in result

@pytest.mark.asyncio
async def test_special_characters_handling() -> None:
    """Test handling of special characters in EDI values."""
    cargo_item = CargoItem(
        cargo_type="FCL",
        number_of_packages=10,
        container_number="CONT'123",
        master_bill_of_lading_number="MBL'456"
    )

    edi_segment = generate_edi_segment(cargo_item)
    assert "CONT?'123" in edi_segment
    assert "MBL?'456" in edi_segment

# Integration Tests

# 1. Single Valid Item Tests
@pytest.mark.asyncio
async def test_generate_edi_single_valid_item(client):
    """Test EDI generation API with a single valid cargo item."""
    response = await client.post("/api/v1/edi/generate", json={
        "items": [VALID_CARGO_ITEM]
    })

    assert response.status_code == 200
    data = response.json()
    assert "edi_content" in data
    assert data["edi_content"]
    assert data.get("errors") is None

    # Verify EDI content format
    edi_content = data["edi_content"]
    expected_segments = [
        "LIN+1+I'",
        "PAC+++FCL:67:95'",
        "PAC+10+1'",
        "PCI+1'",
        "RFF+AAQ:CONT123456'",
        "PCI+1'",
        "RFF+MB:MBL123456'",
        "PCI+1'",
        "RFF+BH:HBL123456'"
    ]
    for segment in expected_segments:
        assert segment in edi_content

# 2. Single Invalid Item Tests
@pytest.mark.asyncio
async def test_generate_edi_single_invalid_item(client):
    """Test EDI generation API with a single invalid cargo item."""
    response = await client.post("/api/v1/edi/generate", json={
        "items": [INVALID_CARGO_ITEM]
    })

    assert response.status_code == 422  # Changed from 400 to 422 for validation errors
    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0
    assert any("cargo_type" in error["message"].lower() for error in data["detail"])

# 3. Multiple Valid Items Tests
@pytest.mark.asyncio
async def test_generate_edi_multiple_valid_items(client):
    """Test EDI generation API with multiple valid cargo items."""
    response = await client.post("/api/v1/edi/generate", json={
        "items": VALID_CARGO_ITEMS
    })

    assert response.status_code == 200
    data = response.json()
    assert "edi_content" in data
    assert data["edi_content"]
    assert data.get("errors") is None

    # Verify both items are included in EDI content
    edi_content = data["edi_content"]
    assert "CONT123456" in edi_content
    assert "CONT789012" in edi_content

# 4. Mixed Valid and Invalid Items Tests
@pytest.mark.asyncio
async def test_generate_edi_mixed_items(client):
    """Test EDI generation API with a mix of valid and invalid cargo items."""
    response = await client.post("/api/v1/edi/generate", json={
        "items": MIXED_CARGO_ITEMS
    })

    assert response.status_code == 200
    data = response.json()
    assert "edi_content" in data
    assert "errors" in data

    # Should have one error for the invalid item
    assert len(data["errors"]) == 1
    error = data["errors"][0]
    assert error["index"] == 1  # Second item in the list

    # Verify valid items are included in EDI content
    edi_content = data["edi_content"]
    assert "CONT123456" in edi_content  # From valid item
    assert "CONT123€" not in edi_content  # From invalid item

# 5. Empty Request Tests
@pytest.mark.asyncio
async def test_generate_edi_empty_request(client):
    """Test EDI generation API with an empty request."""
    response = await client.post("/api/v1/edi/generate", json={
        "items": []
    })

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == EErrorMessage.NO_ITEMS.value

# 6. ASCII Character Validation Tests
@pytest.mark.asyncio
async def test_ascii_character_validation_single_item(client):
    """Test validation of ASCII characters in a single item."""
    item_with_non_ascii = {
        "cargo_type": "FCL",
        "number_of_packages": 1,
        "container_number": "CONT123€",  # Non-ASCII character
        "master_bill_of_lading_number": "MBL123"
    }

    response = await client.post("/api/v1/edi/generate", json={
        "items": [item_with_non_ascii]
    })

    # Should return 422 as there are no valid items
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert len(data["detail"]) > 0
    assert "ascii" in data["detail"][0]["message"].lower()  # Case insensitive check

@pytest.mark.asyncio
async def test_ascii_character_validation_mixed_items(client):
    """Test validation of ASCII characters with mixed valid and invalid items."""
    item_with_non_ascii = {
        "cargo_type": "FCL",
        "number_of_packages": 1,
        "container_number": "CONT123€",  # Non-ASCII character
        "master_bill_of_lading_number": "MBL123"
    }

    valid_item = {
        "cargo_type": "FCL",
        "number_of_packages": 1,
        "container_number": "CONT456",
        "master_bill_of_lading_number": "MBL456"
    }

    response = await client.post("/api/v1/edi/generate", json={
        "items": [item_with_non_ascii, valid_item]
    })

    assert response.status_code == 200
    data = response.json()
    assert "edi_content" in data
    assert data["errors"] is not None
    assert len(data["errors"]) == 1
    assert "ascii" in data["errors"][0]["message"].lower()  # Case insensitive check

# 7. Optional Fields Tests
@pytest.mark.asyncio
async def test_generate_edi_optional_fields(client):
    """Test EDI generation with optional fields omitted."""
    item_with_optional_fields = {
        "cargo_type": "FCL",
        "number_of_packages": 5,
        "container_number": "CONT123"  # Only one reference number
    }

    response = await client.post("/api/v1/edi/generate", json={
        "items": [item_with_optional_fields]
    })

    assert response.status_code == 200
    data = response.json()
    assert "edi_content" in data
    assert data["edi_content"]  # Verify content is not empty
    assert data.get("errors") is None

    # Verify EDI content format
    edi_content = data["edi_content"]
    assert "RFF+AAQ:CONT123" in edi_content
    assert "RFF+MB:" not in edi_content  # Should not include master bill
    assert "RFF+BH:" not in edi_content  # Should not include house bill

# 8. Service Layer Tests
@pytest.mark.asyncio
async def test_generate_edi_message() -> None:
    """Test EDI message generation in service layer."""
    cargo_items = [
        CargoItem(
            cargo_type=ECargoType.FCL,
            number_of_packages=10,
            container_number="CONT123",
            master_bill_of_lading_number="MBL123"
        ),
        CargoItem(
            cargo_type=ECargoType.LCL,
            number_of_packages=5,
            container_number="CONT456",
            house_bill_of_lading_number="HBL456"
        )
    ]

    service = EDIGenerationService()
    edi_content, errors = await service.generate_edi_message(cargo_items)

    assert isinstance(edi_content, str)
    assert len(edi_content) > 0
    assert not errors

    # Verify EDI content format
    assert "LIN+1+I'" in edi_content
    assert "LIN+2+I'" in edi_content
    assert "PAC+++FCL:67:95'" in edi_content
    assert "PAC+++LCL:67:95'" in edi_content
    assert "RFF+AAQ:CONT123" in edi_content
    assert "RFF+AAQ:CONT456" in edi_content

@pytest.mark.asyncio
async def test_generate_edi_message_empty_items() -> None:
    """Test EDI message generation with empty items list."""
    service = EDIGenerationService()
    edi_content, errors = await service.generate_edi_message([])

    assert edi_content is None
    assert len(errors) == 1
    assert errors[0].message == EErrorMessage.NO_ITEMS.value
