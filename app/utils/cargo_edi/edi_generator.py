from typing import TYPE_CHECKING, Optional

from app.constants.cargo import ECargoType

if TYPE_CHECKING:
    from app.models.cargo_item import CargoItem


def escape_quotes(value: Optional[str]) -> str:
    """
    Escape single quotes in EDI values.
    In EDI, single quote (') is the end-of-line delimiter.
    When a single quote appears in the actual value, it needs to be escaped with a question mark (?).
    For example: ABC'345 -> ABC?'345

    If there are consecutive question marks before a quote, they should be reduced to a single one.
    For example: ABC??'123 -> ABC?'123

    The question mark (?) functions as an escape character, so when ?' appears,
    the quote is treated as literal text rather than a delimiter.

    If value is None, returns an empty string.
    """
    if value is None:
        return ""

    # First handle any existing consecutive question marks
    result = value
    while "??" in result:
        result = result.replace("??", "?")

    # Then escape any unescaped quotes
    # If a quote is not preceded by a question mark, escape it
    final = ""
    i = 0
    while i < len(result):
        if result[i] == "'" and (i == 0 or result[i-1] != "?"):
            final += "?'"
        else:
            final += result[i]
        i += 1

    return final


def unescape_quotes(value: str) -> str:
    """
    Unescape single quotes in EDI values.
    In EDI, ?' represents a literal single quote in the value,
    while a single quote without a preceding question mark is the end-of-line delimiter.
    For example: ABC?'345 -> ABC'345
    """
    return value.replace("?'", "'")


def generate_edi_segment(cargo_item: "CargoItem", line_index: int = 1) -> str:
    """
    Generate EDI segment for a cargo item.
    Format:
    LIN+{line index}+I'
    PAC+++{cargo type}:67:95'
    PAC+{number of packages}+1'
    PCI+1'
    RFF+AAQ:{container number}'
    PCI+1'
    RFF+MB:{master bill of lading number}'
    PCI+1'
    RFF+BH:{house bill of lading number}'

    Args:
        cargo_item: The cargo item to generate EDI for
        line_index: The line index in the EDI message

    Returns:
        Generated EDI segment as string
    """
    if isinstance(cargo_item.cargo_type, ECargoType):
        cargo_type = cargo_item.cargo_type.value
    else:
        cargo_type = cargo_item.cargo_type

    # Start with LIN segment
    edi_segment = f"LIN+{line_index}+I'\n"

    # Add cargo type segment
    edi_segment += f"PAC+++{cargo_type}:67:95'\n"

    # Add package count segment
    edi_segment += f"PAC+{cargo_item.number_of_packages}+1'\n"

    # Add container number if present
    container_number = escape_quotes(cargo_item.container_number)
    if container_number:
        edi_segment += "PCI+1'\n"
        edi_segment += f"RFF+AAQ:{container_number}'\n"

    # Add master bill of lading number if present
    mbl = escape_quotes(cargo_item.master_bill_of_lading_number)
    if mbl:
        edi_segment += "PCI+1'\n"
        edi_segment += f"RFF+MB:{mbl}'\n"

    # Add house bill of lading number if present
    hbl = escape_quotes(cargo_item.house_bill_of_lading_number)
    if hbl:
        edi_segment += "PCI+1'\n"
        edi_segment += f"RFF+BH:{hbl}'\n"

    return edi_segment
