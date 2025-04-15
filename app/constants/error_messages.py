"""Error message constants."""

from enum import Enum


class EErrorMessage(str, Enum):
    """Error messages for EDI generation and validation."""

    NO_ITEMS = "No valid items found in the request"
    INVALID_CARGO_TYPE = "Invalid cargo type"
    INVALID_PACKAGE_COUNT = "Number of packages must be greater than 0"
    ERR_ASCII_CHARS = "Only ASCII characters are allowed"
    EMPTY_EDI_CONTENT = "Empty EDI content"
    INVALID_SEGMENT_FORMAT = "Invalid segment format"
    PROCESSING_ERROR = "Error processing request"
    FAILED_TO_STORE = "Failed to store {}: {}"
    UNKNOWN_ERROR = "An unknown error occurred"
    FAILED_TO_GENERATE_SEGMENT = "Failed to generate EDI segment for item {}: {}"

    # EDI Decoding specific errors
    INVALID_SEGMENT_TYPE = "Invalid segment type: {}"
    INVALID_NUMBER_FORMAT = "Invalid number format in package count: {}"
    MISSING_REQUIRED_FIELD = "Missing required field: {}"
    INVALID_REFERENCE_FORMAT = "Invalid reference format in segment: {}"
    INVALID_CARGO_TYPE_FORMAT = "Invalid cargo type format: {}"
