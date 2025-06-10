# app/api/v1/endpoints/invoice_upload.py

import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from app.services.ocr_google import run_google_vision_and_layoutlm
from app.services.validation import validate_invoice_data
from app.db.session import get_db
from app.models.invoice import Invoice  # ✅ make sure this exists

router = APIRouter()

@router.post("/upload", tags=["Invoices"])
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Step 1: Save file
    contents = await file.read()
    filename = file.filename
    file_path = f"temp_uploads/{filename}"
    os.makedirs("temp_uploads", exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        # Step 2: Run Google Vision OCR + LayoutLMv3 pipeline
        fields = run_google_vision_and_layoutlm(file_path)

        # Step 3: Validate extracted fields
        errors = validate_invoice_data(fields)
        if errors:
            return {
                "filename": filename,
                "status": "failed",
                "errors": errors
            }

        # Step 4: Save to DB
        invoice = Invoice(
            filename=filename,
            invoice_number=fields.get("invoice_number"),
            invoice_date=fields.get("invoice_date"),
            due_date=fields.get("due_date"),
            gstin=fields.get("gstin"),
            total=fields.get("total"),
            currency=fields.get("currency"),
            vendor_name=fields.get("vendor_name"),
            vendor_tax_id=fields.get("vendor_tax_id"),
            customer_name=fields.get("customer_name"),
            payment_terms=fields.get("payment_terms")
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        return {
            "filename": filename,
            "status": "success",
            "invoice_id": invoice.id,
            **fields
        }

    except Exception as e:
        return {
            "filename": filename,
            "status": "error",
            "message": str(e)
        }

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
