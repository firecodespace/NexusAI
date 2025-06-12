# app/api/v1/endpoints/invoice_upload.py

import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
import magic  # for file type validation

from app.services.ocr_google import run_google_vision_and_layoutlm
from app.services.validation import validate_invoice_data
from app.db.session import get_db
from app.models.invoice import Invoice  # ✅ make sure this exists

router = APIRouter()

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    'application/pdf': '.pdf',
    'image/jpeg': '.jpg',
    'image/png': '.png'
}

@router.post("/upload", tags=["Invoices"])
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate file size
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
        )
    
    # Validate file type
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(contents)
    
    if file_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_MIME_TYPES.keys())}"
        )
    
    # Save file
    filename = file.filename
    file_path = f"temp_uploads/{filename}"
    os.makedirs("temp_uploads", exist_ok=True)

    try:
        with open(file_path, "wb") as f:
            f.write(contents)

        # Run Google Vision OCR + LayoutLMv3 pipeline
        try:
            fields = run_google_vision_and_layoutlm(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing invoice: {str(e)}"
            )

        # Validate extracted fields
        errors = validate_invoice_data(fields)
        if errors:
            return {
                "filename": filename,
                "status": "failed",
                "errors": errors
            }

        # Save to DB
        try:
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
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error saving invoice to database: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
