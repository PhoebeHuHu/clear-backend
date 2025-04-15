"""Repository for cargo items collection operations."""
from app.constants.error_messages import EErrorMessage
from app.db.database import get_database
from app.models.cargo_item import CargoItem


class CargoRepository:
    """Repository for cargo items collection operations."""

    @staticmethod
    async def create_cargo_items(cargo_items: list[CargoItem]) -> list[str]:
        """Create multiple cargo items in database."""
        db = get_database()
        cargo_item_ids = []

        for item in cargo_items:
            try:

                doc = item.model_dump(exclude_unset=True, exclude_none=True)
                result = await db.cargo_items.insert_one(doc)
                if not result.acknowledged:
                    # If any insert fails, we should probably rollback previous inserts
                    # TODO: Implement rollback mechanism
                    raise Exception(EErrorMessage.FAILED_TO_STORE.value)
                cargo_item_ids.append(str(result.inserted_id))
            except Exception as e:
                raise Exception(EErrorMessage.FAILED_TO_STORE.value) from e

        return cargo_item_ids
