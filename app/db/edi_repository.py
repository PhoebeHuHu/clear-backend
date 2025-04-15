from datetime import UTC, datetime

from app.constants.error_messages import EErrorMessage
from app.db.database import get_database
from app.models.edi_message import EDIMessage


class EDIRepository:
    """Repository for EDI messages collection operations."""

    @staticmethod
    async def store_edi_message(edi_content: str, cargo_item_ids: list[str]) -> bool:
        """
        Store EDI message in database.

        Args:
            edi_content: The EDI message content
            cargo_item_ids: List of related cargo item IDs

        Returns:
            True if storage was successful, False otherwise
        """
        if not edi_content:
            raise ValueError(EErrorMessage.EMPTY_EDI_CONTENT.value)

        edi_doc = EDIMessage(
            edi_content=edi_content,
            cargo_item_ids=cargo_item_ids,
            created_at=datetime.now(UTC)
        )

        db = get_database()
        result = await db.edi_messages.insert_one(edi_doc.model_dump())
        return result.acknowledged
