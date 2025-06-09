from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

from ..services.gst_categorization import GSTCategorizationService, GSTCategorizationResult
from ..services.reconciliation import ReconciliationService, ReconciliationResult
from ..services.analytics import AnalyticsService, FraudDetectionResult, CashFlowPrediction

router = APIRouter(prefix="/gst", tags=["GST"])

# Pydantic models for request/response
class InvoiceData(BaseModel):
    invoice_id: str
    date: str
    gstin: str
    hsn_code: str
    total_amount: float
    tax_amount: float
    vendor_name: str
    items: List[Dict]

class VendorData(BaseModel):
    gstin: str
    name: str
    expected_amount: float
    payment_terms: str

class GSTCategorizationResponse(BaseModel):
    category: str
    hsn_code: str
    confidence_score: float
    validation_notes: List[str]

class ReconciliationResponse(BaseModel):
    status: str
    invoice_id: str
    vendor_gstin: str
    invoice_gstin: str
    amount_matched: bool
    gstin_matched: bool
    validation_notes: List[str]
    confidence_score: float

class FraudDetectionResponse(BaseModel):
    risk_level: str
    invoice_id: str
    vendor_gstin: str
    anomaly_score: float
    detection_reasons: List[str]
    confidence_score: float

class CashFlowPredictionResponse(BaseModel):
    date: str
    predicted_amount: float
    confidence_interval: List[float]
    contributing_factors: List[str]

# Service instances
gst_categorization_service = GSTCategorizationService()
reconciliation_service = ReconciliationService()
analytics_service = AnalyticsService()

@router.post("/categorize")
async def categorize_invoice(invoice_data: InvoiceData):
    """
    Test endpoint for invoice categorization
    """
    return {
        "status": "success",
        "message": "Invoice received",
        "data": invoice_data.dict()
    }

@router.get("/test")
async def test():
    """
    Test endpoint to verify router is working
    """
    return {"status": "GST router is working"}

@router.post("/categorize", response_model=GSTCategorizationResponse)
async def categorize_invoice_real(invoice_data: InvoiceData):
    """
    Categorize an invoice based on its data and HSN/SAC codes
    """
    try:
        result = gst_categorization_service.categorize_invoice(invoice_data.dict())
        return GSTCategorizationResponse(
            category=result.category.value,
            hsn_code=result.hsn_code,
            confidence_score=result.confidence_score,
            validation_notes=result.validation_notes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reconcile", response_model=ReconciliationResponse)
async def reconcile_invoice(
    invoice_data: InvoiceData,
    vendor_data: VendorData
):
    """
    Reconcile an invoice against vendor master data
    """
    try:
        result = reconciliation_service.reconcile_invoice(
            invoice_data.dict(),
            vendor_data.dict()
        )
        return ReconciliationResponse(
            status=result.status.value,
            invoice_id=result.invoice_id,
            vendor_gstin=result.vendor_gstin,
            invoice_gstin=result.invoice_gstin,
            amount_matched=result.amount_matched,
            gstin_matched=result.gstin_matched,
            validation_notes=result.validation_notes,
            confidence_score=result.confidence_score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-fraud", response_model=FraudDetectionResponse)
async def detect_fraud(
    invoice_data: InvoiceData,
    historical_data: List[InvoiceData]
):
    """
    Detect potential fraud in invoice data
    """
    try:
        result = analytics_service.detect_fraud(
            invoice_data.dict(),
            [data.dict() for data in historical_data]
        )
        return FraudDetectionResponse(
            risk_level=result.risk_level.value,
            invoice_id=result.invoice_id,
            vendor_gstin=result.vendor_gstin,
            anomaly_score=result.anomaly_score,
            detection_reasons=result.detection_reasons,
            confidence_score=result.confidence_score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-cash-flow", response_model=List[CashFlowPredictionResponse])
async def predict_cash_flow(
    historical_data: List[InvoiceData],
    prediction_days: Optional[int] = 30
):
    """
    Predict cash flow for the next N days
    """
    try:
        predictions = analytics_service.predict_cash_flow(
            [data.dict() for data in historical_data],
            prediction_days
        )
        return [
            CashFlowPredictionResponse(
                date=pred.date.isoformat(),
                predicted_amount=pred.predicted_amount,
                confidence_interval=list(pred.confidence_interval),
                contributing_factors=pred.contributing_factors
            )
            for pred in predictions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 