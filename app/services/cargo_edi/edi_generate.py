from typing import Any, Optional, Union

from pydantic import ValidationError

from app.constants.error_messages import EErrorMessage
from app.db.cargo_repository import CargoRepository
from app.db.edi_repository import EDIRepository
from app.models.cargo_item import CargoItem
from app.models.responses import ProcessingError
from app.utils.cargo_edi import generate_edi_segment


class EDIGenerationService:
    """Service for generating EDI messages."""

    def __init__(self):
        self.cargo_repository = CargoRepository()
        self.edi_repository = EDIRepository()

    def _validate_cargo_item(
        self,
        cargo_item: Union[dict[str, Any], CargoItem],
        index: int
    ) -> tuple[Optional[CargoItem], list[ProcessingError]]:
        """Validate a cargo item and convert it to CargoItem if needed."""
        try:
            if isinstance(cargo_item, dict):
                cargo_item = CargoItem(**cargo_item)
            return cargo_item, []
        except ValidationError as e:
            return None, [ProcessingError(index=index, message=str(e))]

    async def _store_cargo_items(
        self,
        valid_items: list[CargoItem]
    ) -> tuple[list[str], list[ProcessingError]]:
        """Store cargo items in database and return their IDs."""
        errors = []
        cargo_item_ids = []
        try:
            cargo_item_ids = await self.cargo_repository.create_cargo_items(valid_items)
            # Update items with their IDs
            for item, item_id in zip(valid_items, cargo_item_ids):
                item.id = item_id
        except Exception as e:
            errors.append(ProcessingError(
                message=EErrorMessage.FAILED_TO_STORE.value.format("cargo items", str(e))
            ))
        return cargo_item_ids, errors

    def _generate_edi_segments(
        self,
        valid_items: list[CargoItem]
    ) -> tuple[list[str], list[ProcessingError]]:
        """Generate EDI segments for valid items."""
        errors = []
        segments = []
        for index, item in enumerate(valid_items, start=1):
            try:
                segment = generate_edi_segment(item, index)
                segments.append(segment)
            except Exception as e:
                errors.append(ProcessingError(
                    index=index-1,
                    message=EErrorMessage.FAILED_TO_GENERATE_SEGMENT.value.format(index, str(e))
                ))
        return segments, errors

    async def _store_edi_message(
        self,
        edi_content: str,
        cargo_ids: list[str]
    ) -> list[ProcessingError]:
        """Store EDI message in database."""
        errors = []
        try:
            if cargo_ids and not await self.edi_repository.store_edi_message(edi_content, cargo_ids):
                errors.append(ProcessingError(
                    message=EErrorMessage.FAILED_TO_STORE.value.format(
                        "EDI message",
                        "storage operation failed"
                    )
                ))
        except Exception as e:
            errors.append(ProcessingError(
                message=EErrorMessage.FAILED_TO_STORE.value.format("EDI message", str(e))
            ))
        return errors

    async def generate_edi_message(
        self,
        items: list[Union[dict[str, Any], CargoItem]]
    ) -> tuple[Optional[str], list[ProcessingError]]:
        """Generate EDI message from cargo items and store in database."""
        errors = []
        if not items:
            return None, [ProcessingError(message=EErrorMessage.NO_ITEMS.value)]

        # Validate and convert items
        valid_items = []
        for idx, item in enumerate(items):
            cargo_item, validation_errors = self._validate_cargo_item(item, idx)
            if validation_errors:
                errors.extend(validation_errors)
            if cargo_item:
                valid_items.append(cargo_item)

        # If no valid items were found
        if not valid_items:
            return None, errors

        # Store cargo items and generate EDI segments
        cargo_item_ids, storage_errors = await self._store_cargo_items(valid_items)
        errors.extend(storage_errors)

        segments, generation_errors = self._generate_edi_segments(valid_items)
        errors.extend(generation_errors)

        # If no segments were successfully generated
        if not segments:
            return None, errors

        # Join successful segments
        edi_content = "".join(segments)

        # Store EDI document
        storage_errors = await self._store_edi_message(
            edi_content,
            [str(item.id) for item in valid_items if item.id]
        )
        errors.extend(storage_errors)

        return edi_content, errors
