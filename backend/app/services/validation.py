# app/services/validation.py

import re
from typing import List, Dict

REQUIRED_FIELDS = ["invoice_number", "invoice_date", "gstin", "total"]

def is_valid_gstin(gstin: str) -> bool:
    """
    GSTIN Format: 15 characters
    2-digit state code + 10-character PAN + 1 entity + 1 Z + 1 checksum
    Example: 22AAAAA0000A1Z5
    """
    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    return bool(re.match(pattern, gstin.strip()))


def is_valid_date(date_str: str) -> bool:
    """Basic date format checker (dd/mm/yyyy or dd-mm-yyyy)."""
    return bool(re.match(r"\d{2}[\/\-.]\d{2}[\/\-.]\d{4}", date_str.strip()))


def is_valid_amount(value: str) -> bool:
    """Check if value is a valid number with decimal."""
    return bool(re.match(r"[\d,]+\.\d{2}", value.strip()))


def validate_invoice_data(data: Dict[str, str]) -> List[str]:
    """
    Validate extracted invoice fields.
    Returns a list of errors if found.
    """
    errors = []

    # Check for missing required fields
    for field in REQUIRED_FIELDS:
        if not data.get(field) or data[field] == "N/A":
            errors.append(f"Missing required field: {field}")

    # GSTIN format
    gstin = data.get("gstin")
    if gstin and gstin != "N/A" and not is_valid_gstin(gstin):
        errors.append(f"Invalid GSTIN format: {gstin}")

    # Date formats
    invoice_date = data.get("invoice_date")
    if invoice_date and not is_valid_date(invoice_date):
        errors.append(f"Invalid invoice date format: {invoice_date}")

    # Amount
    total = data.get("total")
    if total and not is_valid_amount(total):
        errors.append(f"Invalid total amount: {total}")

    return errors
