from app.services.validation import validate_invoice_data

extracted = {
    "invoice_number": "INV-123",
    "invoice_date": "01/06/2025",
    "gstin": "22AAAAA0000A1Z5",
    "total": "4,999.00"
}

errors = validate_invoice_data(extracted)
if errors:
    print("❌ Validation errors:")
    for err in errors:
        print(" -", err)
else:
    print("✅ All fields are valid.")