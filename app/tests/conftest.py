import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings
from app.db.database import client as app_client  # Import the client from app
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Get test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
async def mongodb() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Get MongoDB client."""
    yield app_client  # Use the same client instance as the app


@pytest.fixture(scope="session")
async def db(mongodb) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get test database."""
    database = mongodb[settings.MONGODB_DB_NAME + "_test"]
    yield database
    await mongodb.drop_database(settings.MONGODB_DB_NAME + "_test")


@pytest.fixture(autouse=True)
async def setup_db(db):
    """Setup test database before each test."""
    # Clear all collections before each test
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})
    yield
