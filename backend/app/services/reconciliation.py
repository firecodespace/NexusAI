from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReconciliationStatus(Enum):
    MATCHED = "MATCHED"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    MISMATCH = "MISMATCH"
    PENDING = "PENDING"

@dataclass
class ReconciliationResult:
    status: ReconciliationStatus
    invoice_id: str
    vendor_gstin: str
    invoice_gstin: str
    amount_matched: bool
    gstin_matched: bool
    validation_notes: List[str]
    confidence_score: float

class ReconciliationService:
    def __init__(self):
        self.vendor_master = {}  # Will be populated from database
        
    def reconcile_invoice(self, invoice_data: Dict, vendor_data: Dict) -> ReconciliationResult:
        """
        Reconcile an invoice against vendor master data
        
        Args:
            invoice_data: Dictionary containing invoice details
            vendor_data: Dictionary containing vendor master data
            
        Returns:
            ReconciliationResult containing reconciliation status and details
        """
        validation_notes = []
        confidence_score = 0.0
        
        # Extract GSTINs
        invoice_gstin = invoice_data.get('gstin', '')
        vendor_gstin = vendor_data.get('gstin', '')
        
        # Check GSTIN match
        gstin_matched = self._validate_gstin_match(invoice_gstin, vendor_gstin)
        if not gstin_matched:
            validation_notes.append(f"GSTIN mismatch: Invoice {invoice_gstin} vs Vendor {vendor_gstin}")
            
        # Check amount match
        amount_matched = self._validate_amount_match(invoice_data, vendor_data)
        if not amount_matched:
            validation_notes.append("Amount mismatch detected")
            
        # Determine reconciliation status
        status = self._determine_reconciliation_status(gstin_matched, amount_matched)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            gstin_matched, 
            amount_matched,
            invoice_data,
            vendor_data
        )
        
        return ReconciliationResult(
            status=status,
            invoice_id=invoice_data.get('invoice_id', ''),
            vendor_gstin=vendor_gstin,
            invoice_gstin=invoice_gstin,
            amount_matched=amount_matched,
            gstin_matched=gstin_matched,
            validation_notes=validation_notes,
            confidence_score=confidence_score
        )
        
    def _validate_gstin_match(self, invoice_gstin: str, vendor_gstin: str) -> bool:
        """Validate if GSTINs match"""
        if not invoice_gstin or not vendor_gstin:
            return False
            
        # Basic format validation
        if not self._is_valid_gstin_format(invoice_gstin) or not self._is_valid_gstin_format(vendor_gstin):
            return False
            
        return invoice_gstin == vendor_gstin
        
    def _validate_amount_match(self, invoice_data: Dict, vendor_data: Dict) -> bool:
        """Validate if amounts match within tolerance"""
        # Handle None values and use correct field name
        invoice_amount_raw = invoice_data.get('amount', 0)
        vendor_amount_raw = vendor_data.get('expected_amount', 0)
        
        # Convert to float safely
        try:
            invoice_amount = float(invoice_amount_raw) if invoice_amount_raw is not None else 0.0
            vendor_amount = float(vendor_amount_raw) if vendor_amount_raw is not None else 0.0
        except (ValueError, TypeError):
            # If conversion fails, return False
            return False
        
        # Define tolerance (e.g., 0.1% difference allowed)
        tolerance = 0.001
        difference = abs(invoice_amount - vendor_amount)
        
        return difference <= (vendor_amount * tolerance)
        
    def _determine_reconciliation_status(
        self, 
        gstin_matched: bool, 
        amount_matched: bool
    ) -> ReconciliationStatus:
        """Determine reconciliation status based on matches"""
        if gstin_matched and amount_matched:
            return ReconciliationStatus.MATCHED
        elif gstin_matched or amount_matched:
            return ReconciliationStatus.PARTIAL_MATCH
        else:
            return ReconciliationStatus.MISMATCH
            
    def _calculate_confidence_score(
        self,
        gstin_matched: bool,
        amount_matched: bool,
        invoice_data: Dict,
        vendor_data: Dict
    ) -> float:
        """Calculate confidence score for reconciliation"""
        score = 0.0
        
        # Base scores for matches
        if gstin_matched:
            score += 0.6
        if amount_matched:
            score += 0.4
            
        # Additional validation factors
        if self._validate_invoice_date(invoice_data, vendor_data):
            score += 0.1
        if self._validate_vendor_name(invoice_data, vendor_data):
            score += 0.1
            
        return min(score, 1.0)
        
    def _is_valid_gstin_format(self, gstin: str) -> bool:
        """Validate GSTIN format"""
        # GSTIN format: 2 digits state code + 10 digits PAN + 1 digit entity number + 1 check digit
        if not gstin or len(gstin) != 15:
            return False
            
        # Add more detailed validation if needed
        return True
        
    def _validate_invoice_date(self, invoice_data: Dict, vendor_data: Dict) -> bool:
        """Validate if invoice date is within expected range"""
        # Implement date validation logic
        return True
        
    def _validate_vendor_name(self, invoice_data: Dict, vendor_data: Dict) -> bool:
        """Validate if vendor names match"""
        # Implement vendor name matching logic
        return True 