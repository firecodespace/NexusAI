from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class FraudRiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class FraudDetectionResult:
    risk_level: FraudRiskLevel
    invoice_id: str
    vendor_gstin: str
    anomaly_score: float
    detection_reasons: List[str]
    confidence_score: float

@dataclass
class CashFlowPrediction:
    date: datetime
    predicted_amount: float
    confidence_interval: Tuple[float, float]
    contributing_factors: List[str]

class AnalyticsService:
    def __init__(self):
        self.fraud_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def detect_fraud(self, invoice_data: Dict, historical_data: List[Dict]) -> FraudDetectionResult:
        """
        Detect potential fraud in invoice data
        
        Args:
            invoice_data: Dictionary containing invoice details
            historical_data: List of historical invoice data for comparison
            
        Returns:
            FraudDetectionResult containing fraud risk assessment
        """
        detection_reasons = []
        confidence_score = 0.0
        
        # Extract features for fraud detection
        features = self._extract_fraud_features(invoice_data, historical_data)
        
        # Calculate anomaly score
        anomaly_score = self._calculate_anomaly_score(features)
        
        # Check for specific fraud patterns
        if self._check_duplicate_gstin(invoice_data, historical_data):
            detection_reasons.append("Duplicate GSTIN detected")
            confidence_score += 0.3
            
        if self._check_abnormal_amount(invoice_data, historical_data):
            detection_reasons.append("Abnormal invoice amount")
            confidence_score += 0.3
            
        if self._check_suspicious_vendor_pattern(invoice_data, historical_data):
            detection_reasons.append("Suspicious vendor pattern detected")
            confidence_score += 0.4
            
        # Determine risk level
        risk_level = self._determine_risk_level(anomaly_score, confidence_score)
        
        return FraudDetectionResult(
            risk_level=risk_level,
            invoice_id=invoice_data.get('invoice_id', ''),
            vendor_gstin=invoice_data.get('gstin', ''),
            anomaly_score=anomaly_score,
            detection_reasons=detection_reasons,
            confidence_score=confidence_score
        )
        
    def predict_cash_flow(
        self,
        historical_data: List[Dict],
        prediction_days: int = 30
    ) -> List[CashFlowPrediction]:
        """
        Predict cash flow for the next N days
        
        Args:
            historical_data: List of historical transaction data
            prediction_days: Number of days to predict ahead
            
        Returns:
            List of CashFlowPrediction objects
        """
        predictions = []
        
        # Prepare historical data
        dates, amounts = self._prepare_historical_data(historical_data)
        
        # Calculate basic statistics
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        
        # Generate predictions
        for i in range(prediction_days):
            prediction_date = dates[-1] + timedelta(days=i+1)
            
            # Simple moving average prediction
            predicted_amount = self._calculate_moving_average(amounts, window=7)
            
            # Calculate confidence interval
            confidence_interval = (
                predicted_amount - 1.96 * std_amount,
                predicted_amount + 1.96 * std_amount
            )
            
            # Identify contributing factors
            contributing_factors = self._identify_contributing_factors(
                historical_data,
                prediction_date
            )
            
            predictions.append(CashFlowPrediction(
                date=prediction_date,
                predicted_amount=predicted_amount,
                confidence_interval=confidence_interval,
                contributing_factors=contributing_factors
            ))
            
        return predictions
        
    def _extract_fraud_features(
        self,
        invoice_data: Dict,
        historical_data: List[Dict]
    ) -> np.ndarray:
        """Extract features for fraud detection"""
        features = []
        
        # Amount-based features
        features.append(float(invoice_data.get('total_amount', 0)))
        features.append(float(invoice_data.get('tax_amount', 0)))
        
        # Time-based features
        invoice_date = datetime.fromisoformat(invoice_data.get('date', ''))
        features.append(invoice_date.weekday())
        features.append(invoice_date.day)
        
        # Vendor-based features
        vendor_history = [d for d in historical_data if d.get('gstin') == invoice_data.get('gstin')]
        features.append(len(vendor_history))
        
        return np.array(features).reshape(1, -1)
        
    def _calculate_anomaly_score(self, features: np.ndarray) -> float:
        """Calculate anomaly score using Isolation Forest"""
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Calculate anomaly score
        score = self.fraud_detector.fit_predict(scaled_features)
        return float(score[0])
        
    def _check_duplicate_gstin(
        self,
        invoice_data: Dict,
        historical_data: List[Dict]
    ) -> bool:
        """Check for duplicate GSTIN usage"""
        invoice_gstin = invoice_data.get('gstin')
        invoice_date = datetime.fromisoformat(invoice_data.get('date', ''))
        
        # Look for same GSTIN used on same day
        for data in historical_data:
            if (data.get('gstin') == invoice_gstin and
                datetime.fromisoformat(data.get('date', '')) == invoice_date):
                return True
                
        return False
        
    def _check_abnormal_amount(
        self,
        invoice_data: Dict,
        historical_data: List[Dict]
    ) -> bool:
        """Check for abnormal invoice amounts"""
        amount = float(invoice_data.get('total_amount', 0))
        amounts = [float(d.get('total_amount', 0)) for d in historical_data]
        
        if not amounts:
            return False
            
        mean = np.mean(amounts)
        std = np.std(amounts)
        
        # Flag if amount is more than 3 standard deviations from mean
        return abs(amount - mean) > 3 * std
        
    def _check_suspicious_vendor_pattern(
        self,
        invoice_data: Dict,
        historical_data: List[Dict]
    ) -> bool:
        """Check for suspicious vendor patterns"""
        vendor_gstin = invoice_data.get('gstin')
        vendor_history = [d for d in historical_data if d.get('gstin') == vendor_gstin]
        
        if len(vendor_history) < 3:
            return False
            
        # Check for unusual frequency of invoices
        dates = [datetime.fromisoformat(d.get('date', '')) for d in vendor_history]
        date_diffs = np.diff([d.timestamp() for d in dates])
        
        return np.std(date_diffs) < np.mean(date_diffs) * 0.5
        
    def _determine_risk_level(
        self,
        anomaly_score: float,
        confidence_score: float
    ) -> FraudRiskLevel:
        """Determine fraud risk level"""
        if anomaly_score < -0.5 and confidence_score > 0.6:
            return FraudRiskLevel.HIGH
        elif anomaly_score < -0.3 or confidence_score > 0.4:
            return FraudRiskLevel.MEDIUM
        else:
            return FraudRiskLevel.LOW
            
    def _prepare_historical_data(
        self,
        historical_data: List[Dict]
    ) -> Tuple[List[datetime], List[float]]:
        """Prepare historical data for cash flow prediction"""
        dates = []
        amounts = []
        
        for data in historical_data:
            dates.append(datetime.fromisoformat(data.get('date', '')))
            amounts.append(float(data.get('total_amount', 0)))
            
        return dates, amounts
        
    def _calculate_moving_average(self, amounts: List[float], window: int = 7) -> float:
        """Calculate moving average of amounts"""
        if len(amounts) < window:
            return np.mean(amounts)
            
        return np.mean(amounts[-window:])
        
    def _identify_contributing_factors(
        self,
        historical_data: List[Dict],
        prediction_date: datetime
    ) -> List[str]:
        """Identify factors contributing to cash flow prediction"""
        factors = []
        
        # Check for seasonal patterns
        if prediction_date.month in [3, 9]:  # Quarter ends
            factors.append("Quarter-end effect")
            
        # Check for vendor payment patterns
        vendor_payments = self._analyze_vendor_payments(historical_data)
        if vendor_payments:
            factors.append(f"Vendor payment pattern: {vendor_payments}")
            
        return factors
        
    def _analyze_vendor_payments(self, historical_data: List[Dict]) -> str:
        """Analyze vendor payment patterns"""
        # Implement vendor payment pattern analysis
        return "Regular monthly payments" 