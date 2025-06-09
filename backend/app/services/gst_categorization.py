from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging
import os

logger = logging.getLogger(__name__)

class GSTCategory(Enum):
    NIL = "NIL"
    EXEMPT = "EXEMPT"
    ZERO = "0%"
    FIVE = "5%"
    TWELVE = "12%"
    EIGHTEEN = "18%"
    TWENTY_EIGHT = "28%"

@dataclass
class GSTCategorizationResult:
    category: GSTCategory
    hsn_code: str
    confidence_score: float
    validation_notes: List[str]

class GSTCategorizationService:
    def __init__(self):
        self.hsn_mapping = self._load_hsn_mapping()
        
    def _load_hsn_mapping(self) -> Dict[str, Dict]:
        """Load HSN code mapping from JSON file"""
        try:
            # Get the absolute path to the data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(os.path.dirname(current_dir), 'data')
            mapping_file = os.path.join(data_dir, 'hsn_mapping.json')
            
            if not os.path.exists(mapping_file):
                logger.warning(f"HSN mapping file not found at {mapping_file}")
                return {}
                
            with open(mapping_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading HSN mapping: {str(e)}")
            return {}
            
    def categorize_invoice(self, invoice_data: Dict) -> GSTCategorizationResult:
        """
        Categorize an invoice based on its data and HSN/SAC codes
        """
        validation_notes = []
        confidence_score = 0.0
        
        # Extract HSN code from invoice data
        hsn_code = invoice_data.get('hsn_code')
        if not hsn_code:
            validation_notes.append("No HSN code found in invoice")
            return GSTCategorizationResult(
                category=GSTCategory.NIL,
                hsn_code="",
                confidence_score=0.0,
                validation_notes=validation_notes
            )
            
        # Look up HSN code in mapping
        hsn_info = self.hsn_mapping.get(hsn_code)
        if not hsn_info:
            validation_notes.append(f"HSN code {hsn_code} not found in mapping")
            return GSTCategorizationResult(
                category=GSTCategory.NIL,
                hsn_code=hsn_code,
                confidence_score=0.0,
                validation_notes=validation_notes
            )
            
        # Determine GST category
        category = self._determine_category(hsn_info, invoice_data)
        confidence_score = self._calculate_confidence_score(hsn_info, invoice_data)
        
        return GSTCategorizationResult(
            category=category,
            hsn_code=hsn_code,
            confidence_score=confidence_score,
            validation_notes=validation_notes
        )
        
    def _determine_category(self, hsn_info: Dict, invoice_data: Dict) -> GSTCategory:
        """Determine GST category based on HSN info and invoice data"""
        # Default category from HSN mapping
        category = GSTCategory(hsn_info.get('default_category', 'NIL'))
        
        # Apply special rules and exceptions
        if self._is_exempt_condition(invoice_data):
            category = GSTCategory.EXEMPT
        elif self._is_zero_rated_condition(invoice_data):
            category = GSTCategory.ZERO
            
        return category
        
    def _calculate_confidence_score(self, hsn_info: Dict, invoice_data: Dict) -> float:
        """Calculate confidence score for the categorization"""
        score = 0.0
        
        # Base score from HSN mapping reliability
        score += hsn_info.get('reliability_score', 0.0)
        
        # Additional points for matching conditions
        if self._has_matching_description(hsn_info, invoice_data):
            score += 0.2
        if self._has_matching_amount_range(hsn_info, invoice_data):
            score += 0.3
            
        return min(score, 1.0)
        
    def _is_exempt_condition(self, invoice_data: Dict) -> bool:
        """Check if invoice qualifies for exemption"""
        return False
        
    def _is_zero_rated_condition(self, invoice_data: Dict) -> bool:
        """Check if invoice qualifies for zero rating"""
        return False
        
    def _has_matching_description(self, hsn_info: Dict, invoice_data: Dict) -> bool:
        """Check if invoice description matches HSN description"""
        return False
        
    def _has_matching_amount_range(self, hsn_info: Dict, invoice_data: Dict) -> bool:
        """Check if invoice amount falls within expected range for HSN code"""
        return False