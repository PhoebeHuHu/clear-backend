"""Tests for EDI generation controller."""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.constants.error_messages import EErrorMessage
from app.tests.test_data import SAMPLE_CARGO_ITEMS


@pytest.mark.asyncio
async def test_generate_edi_empty_request(client: AsyncClient):
    """Test generating EDI with empty request."""
    response = await client.post("/api/v1/edi/generate", json={"items": []})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EErrorMessage.NO_ITEMS.value


@pytest.mark.asyncio
async def test_generate_edi_success(client: AsyncClient):
    """Test successful EDI generation."""
    response = await client.post("/api/v1/edi/generate", json={"items": SAMPLE_CARGO_ITEMS})
    assert response.status_code == status.HTTP_200_OK
    assert "edi_content" in response.json()
    assert response.json()["errors"] is None


@pytest.mark.asyncio
async def test_generate_edi_partial_success(client: AsyncClient):
    """Test EDI generation with some invalid items."""
    invalid_items = [{"cargo_type": "INVALID", "number_of_packages": 1}, *SAMPLE_CARGO_ITEMS]
    response = await client.post("/api/v1/edi/generate", json={"items": invalid_items})
    assert response.status_code == status.HTTP_200_OK
    assert "edi_content" in response.json()
    assert response.json()["errors"] is not None
    assert len(response.json()["errors"]) == 1
    assert response.json()["errors"][0]["index"] == 0


@pytest.mark.asyncio
async def test_generate_edi_all_invalid(client: AsyncClient):
    """Test EDI generation with all invalid items."""
    invalid_items = [
        {"cargo_type": "INVALID1", "number_of_packages": 1},
        {"cargo_type": "INVALID2", "number_of_packages": 2},
    ]
    response = await client.post("/api/v1/edi/generate", json={"items": invalid_items})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert isinstance(response.json()["detail"], list)
    assert len(response.json()["detail"]) == 2
