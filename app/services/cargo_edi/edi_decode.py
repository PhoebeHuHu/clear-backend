"""Service for decoding EDI messages."""

from app.constants.error_messages import EErrorMessage
from app.db.cargo_repository import CargoRepository
from app.db.edi_repository import EDIRepository
from app.models.cargo_item import CargoItem
from app.models.responses import ProcessingError
from app.utils.cargo_edi.message_processor import parse_edi_message
from app.utils.validation import validate_ascii_characters


class EDIDecodingService:
    """Service for decoding EDI messages."""

    def __init__(self, cargo_repository: CargoRepository, edi_repository: EDIRepository):
        """Initialize with required repositories."""
        self.cargo_repository = cargo_repository
        self.edi_repository = edi_repository

    async def decode_edi_message(self, edi_content: str) -> tuple[list[CargoItem], list[ProcessingError]]:
        """
        Decode an EDI message into a list of cargo items.

        Args:
            edi_content: The EDI message string to decode

        Returns:
            Tuple containing:
            - List of decoded cargo items
            - List of any errors encountered during decoding
        """
        if not edi_content:
            return [], [ProcessingError(message=EErrorMessage.NO_ITEMS.value)]

        # Validate ASCII characters first
        validation_errors = validate_ascii_characters(edi_content)
        if validation_errors:
            return [], [
                ProcessingError(message=error["error"], index=error.get("index")) for error in validation_errors
            ]

        try:
            cargo_items, errors = parse_edi_message(edi_content)

            # Store valid cargo items in database if any were parsed
            if cargo_items:
                try:
                    # Store all cargo items at once
                    cargo_ids = await self.cargo_repository.create_cargo_items(cargo_items)
                    # Update items with their IDs
                    for item, item_id in zip(cargo_items, cargo_ids):
                        item.id = item_id

                    # Store EDI content with references to cargo items
                    try:
                        await self.edi_repository.store_edi_message(edi_content, cargo_ids)
                    except Exception as e:
                        errors.append(
                            ProcessingError(message=EErrorMessage.FAILED_TO_STORE.value.format("EDI message", str(e)))
                        )
                except Exception as e:
                    errors.append(
                        ProcessingError(message=EErrorMessage.FAILED_TO_STORE.value.format("cargo items", str(e)))
                    )

            # Convert any errors to ProcessingError format if they're not already
            formatted_errors = []
            for error in errors:
                if isinstance(error, ProcessingError):
                    formatted_errors.append(error)
                else:
                    formatted_errors.append(ProcessingError(message=error["error"], index=error.get("index")))

            return cargo_items, formatted_errors

        except Exception as e:
            return [], [ProcessingError(message=f"{EErrorMessage.PROCESSING_ERROR}: {str(e)}")]
