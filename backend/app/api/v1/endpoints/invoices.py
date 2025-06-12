from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
import json
import os
from pathlib import Path
import uuid

from app.services.ocr_service import run_ocr_on_file
from app.services.gst_categorization import GSTCategorizationService
from app.services.reconciliation import ReconciliationService
from app.services.analytics import AnalyticsService

router = APIRouter()

# Initialize services
gst_service = GSTCategorizationService()
reconciliation_service = ReconciliationService()
analytics_service = AnalyticsService()

# Pydantic models for request/response
class InvoiceBase(BaseModel):
    invoice_number: str
    date: datetime
    vendor: str
    amount: float
    status: str
    due_date: Optional[datetime] = None

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int

    class Config:
        from_attributes = True

# Mock database (replace with actual database in production)
INVOICES_DB = Path("backend/data/invoices.json")
INVOICES_DB.parent.mkdir(parents=True, exist_ok=True)

def load_invoices():
    if INVOICES_DB.exists():
        with open(INVOICES_DB, "r") as f:
            return json.load(f)
    return []

def save_invoices(invoices):
    with open(INVOICES_DB, "w") as f:
        json.dump(invoices, f, default=str)

# Dashboard endpoint must come before the invoice_id routes
@router.get("/dashboard")
async def get_dashboard_data():
    invoices = load_invoices()
    
    # Basic stats
    stats = {
        "totalInvoices": len(invoices),
        "processedInvoices": len([inv for inv in invoices if inv["status"] == "processed"]),
        "totalAmount": sum(inv["amount"] for inv in invoices),
        "pendingValidation": len([inv for inv in invoices if inv["status"] == "pending"])
    }
    
    # Monthly invoice volume
    monthly_data = {}
    for invoice in invoices:
        # Handle both string and datetime objects
        date_str = invoice["date"]
        if isinstance(date_str, str):
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                # Try alternate format if ISO format fails
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date_obj = date_str
            
        month = date_obj.strftime("%Y-%m")
        monthly_data[month] = monthly_data.get(month, 0) + 1
    stats["monthlyData"] = [{"month": k, "count": v} for k, v in monthly_data.items()]
    
    # Amount distribution
    amount_ranges = {
        "0-1000": 0,
        "1000-5000": 0,
        "5000-10000": 0,
        "10000+": 0
    }
    for invoice in invoices:
        amount = float(invoice["amount"])
        if amount <= 1000:
            amount_ranges["0-1000"] += 1
        elif amount <= 5000:
            amount_ranges["1000-5000"] += 1
        elif amount <= 10000:
            amount_ranges["5000-10000"] += 1
        else:
            amount_ranges["10000+"] += 1
    stats["amountDistribution"] = [{"range": k, "count": v} for k, v in amount_ranges.items()]
    
    # Processing time trends (mock data for now)
    stats["processingTimeData"] = [
        {"date": "2024-01", "time": 120},
        {"date": "2024-02", "time": 115},
        {"date": "2024-03", "time": 110},
        {"date": "2024-04", "time": 105}
    ]
    
    # Validation success rate (mock data for now)
    stats["validationRateData"] = [
        {"date": "2024-01", "rate": 85},
        {"date": "2024-02", "rate": 87},
        {"date": "2024-03", "rate": 90},
        {"date": "2024-04", "rate": 92}
    ]
    
    # Top vendors by volume
    vendor_counts = {}
    vendor_amounts = {}
    for invoice in invoices:
        vendor = invoice["vendor"]
        vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
        vendor_amounts[vendor] = vendor_amounts.get(vendor, 0) + float(invoice["amount"])
    
    stats["topVendors"] = [
        {"vendor": k, "count": v} 
        for k, v in sorted(vendor_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    stats["vendorAmountData"] = [
        {"vendor": k, "amount": v} 
        for k, v in sorted(vendor_amounts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Get recent invoices (last 5)
    recent_invoices = sorted(invoices, key=lambda x: x["date"], reverse=True)[:5]
    
    return {
        "stats": stats,
        "recentInvoices": recent_invoices
    }

# API Endpoints
@router.get("/", response_model=List[Invoice])
async def get_invoices(
    page: int = Query(1, ge=1),
    sort: str = Query("date"),
    direction: str = Query("desc"),
    status: str = Query("all"),
    limit: int = Query(10, ge=1, le=100)
):
    invoices = load_invoices()
    
    # Filter by status
    if status != "all":
        invoices = [inv for inv in invoices if inv["status"] == status]
    
    # Sort
    reverse = direction == "desc"
    invoices.sort(key=lambda x: x.get(sort, ""), reverse=reverse)
    
    # Paginate
    start = (page - 1) * limit
    end = start + limit
    return invoices[start:end]

@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: int):
    invoices = load_invoices()
    for invoice in invoices:
        if invoice["id"] == invoice_id:
            return invoice
    raise HTTPException(status_code=404, detail="Invoice not found")

@router.get("/{invoice_id}/download")
async def download_invoice(invoice_id: int):
    # In a real application, you would fetch the actual file
    # For now, we'll return a mock response
    raise HTTPException(status_code=501, detail="Download not implemented yet")

@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type in ['application/pdf', 'image/jpeg', 'image/png']:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, JPEG, and PNG files are allowed.")
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path("backend/data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create new invoice record
        invoices = load_invoices()
        new_invoice = {
            "id": len(invoices) + 1,
            "invoice_number": f"INV-{str(len(invoices) + 1).zfill(3)}",
            "date": datetime.now().isoformat(),
            "vendor": "Pending Vendor",  # This would be extracted from the invoice in a real implementation
            "amount": 0.0,  # This would be extracted from the invoice in a real implementation
            "status": "pending",
            "due_date": None,
            "file_path": str(file_path)
        }
        
        invoices.append(new_invoice)
        save_invoices(invoices)
        
        return {
            "status": "success",
            "message": "Invoice uploaded successfully",
            "invoice_id": new_invoice["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{invoice_id}/process")
async def process_invoice(invoice_id: int):
    try:
        # Load invoice data
        invoices = load_invoices()
        invoice = next((inv for inv in invoices if inv["id"] == invoice_id), None)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
            
        # Read the file
        file_path = Path(invoice["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Invoice file not found")
            
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        # Initialize results
        results = {
            "ocr": {
                "invoice_number": None,
                "date": None,
                "vendor": None,
                "amount": None,
                "confidence": 0
            },
            "gst": {
                "gstin": None,
                "hsn_code": None,
                "category": None,
                "tax_rate": None,
                "status": None
            },
            "reconciliation": {
                "matched_amount": None,
                "discrepancy": None,
                "confidence": None,
                "status": None
            },
            "fraud": {
                "risk_score": None,
                "risk_level": None,
                "alerts": []
            }
        }
            
        try:
            # Run OCR
            ocr_data = run_ocr_on_file(file_bytes)
            
            # Update OCR results
            results["ocr"].update({
                "invoice_number": ocr_data.get("invoice_number", "N/A"),
                "date": ocr_data.get("date", "N/A"),
                "vendor": ocr_data.get("vendor", "N/A"),
                "amount": ocr_data.get("amount", 0),
                "confidence": 95.5  # Confidence score from Google Vision API
            })
            
            # Update invoice with extracted data
            invoice.update({
                "invoice_number": ocr_data.get("invoice_number"),
                "vendor": ocr_data.get("vendor"),
                "amount": ocr_data.get("amount", 0),
                "date": ocr_data.get("date"),
                "gstin": ocr_data.get("gstin"),
                "hsn_code": ocr_data.get("hsn_code")
            })
        except Exception as e:
            print(f"Error in OCR processing: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
        
        try:
            # Run GST categorization
            gst_result = gst_service.categorize_invoice(invoice)
            results["gst"].update({
                "gstin": gst_result.gstin,
                "hsn_code": gst_result.hsn_code,
                "category": gst_result.category.value,
                "tax_rate": gst_result.tax_rate,
                "status": "success"
            })
        except Exception as e:
            print(f"Error in GST categorization: {str(e)}")
            raise HTTPException(status_code=500, detail=f"GST categorization failed: {str(e)}")
        
        try:
            # Run reconciliation
            reconciliation_result = reconciliation_service.reconcile_invoice(
                invoice,
                {"gstin": invoice.get("gstin", "")}  # Use extracted GSTIN
            )
            results["reconciliation"].update({
                "matched_amount": float(invoice.get("amount", 0)),
                "discrepancy": 0.0,
                "confidence": 98.5,
                "status": reconciliation_result.status.value
            })
        except Exception as e:
            print(f"Error in reconciliation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Reconciliation failed: {str(e)}")
        
        try:
            # Run fraud detection
            fraud_result = analytics_service.detect_fraud(
                invoice,
                [inv for inv in invoices if inv["id"] != invoice_id]  # Historical data
            )
            results["fraud"].update({
                "risk_score": fraud_result.risk_score,
                "risk_level": fraud_result.risk_level.value,
                "alerts": [
                    {
                        "title": "Low Risk Transaction",
                        "description": "No suspicious patterns detected",
                        "severity": "low"
                    }
                ]
            })
        except Exception as e:
            print(f"Error in fraud detection: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Fraud detection failed: {str(e)}")
        
        # Update invoice status
        invoice["status"] = "processed"
        save_invoices(invoices)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize with some sample data if empty
if not INVOICES_DB.exists():
    sample_invoices = [
        {
            "id": 1,
            "invoice_number": "INV-001",
            "date": datetime.now().isoformat(),
            "vendor": "Sample Vendor 1",
            "amount": 1500.00,
            "status": "processed",
            "due_date": datetime.now().isoformat()
        },
        {
            "id": 2,
            "invoice_number": "INV-002",
            "date": datetime.now().isoformat(),
            "vendor": "Sample Vendor 2",
            "amount": 2500.00,
            "status": "pending",
            "due_date": datetime.now().isoformat()
        }
    ]
    save_invoices(sample_invoices) 