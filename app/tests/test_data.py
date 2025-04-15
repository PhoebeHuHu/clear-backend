"""Test data for EDI tests."""

# Sample cargo items for testing
SAMPLE_CARGO_ITEMS = [
    {
        "cargo_type": "FCL",
        "number_of_packages": 10,
        "container_number": "CONT123456",
        "master_bill_of_lading_number": "MBL123456",
        "house_bill_of_lading_number": "HBL123456"
    },
    {
        "cargo_type": "LCL",
        "number_of_packages": 5,
        "container_number": "CONT789012",
        "master_bill_of_lading_number": "MBL789012",
        "house_bill_of_lading_number": "HBL789012"
    }
]
