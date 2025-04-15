import sys
from typing import cast

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from pymongo.server_api import ServerApi

from app.config import settings

# Create a new client and connect to the server
client = AsyncIOMotorClient(settings.MONGODB_URI, server_api=ServerApi('1'))

# Get the database
_is_test = 'pytest' in sys.modules
db = client[settings.MONGODB_DB_NAME + "_test" if _is_test else settings.MONGODB_DB_NAME]


async def connect_to_mongo() -> None:
    """Connect to MongoDB."""
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
    except ConnectionFailure as e:
        print("❌ MongoDB connection failed!")
        raise ConnectionFailure("Failed to connect to MongoDB") from e


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return cast(AsyncIOMotorDatabase, db)
