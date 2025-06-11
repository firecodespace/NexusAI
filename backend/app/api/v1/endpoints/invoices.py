from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json
import os
from pathlib import Path

router = APIRouter()

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
    
    stats = {
        "totalInvoices": len(invoices),
        "processedInvoices": len([inv for inv in invoices if inv["status"] == "processed"]),
        "totalAmount": sum(inv["amount"] for inv in invoices),
        "pendingValidation": len([inv for inv in invoices if inv["status"] == "pending"])
    }
    
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