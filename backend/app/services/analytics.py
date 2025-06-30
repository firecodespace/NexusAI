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

class GSTComplianceStatus(Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PENDING = "PENDING"
    WARNING = "WARNING"

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

@dataclass
class CashFlowAnalysis:
    total_inflow: float
    total_outflow: float
    net_cash_flow: float
    average_daily_flow: float
    cash_flow_trend: str  # "increasing", "decreasing", "stable"
    monthly_breakdown: List[Dict[str, any]]
    cash_flow_forecast: List[CashFlowPrediction]
    risk_factors: List[str]

@dataclass
class GSTComplianceAnalysis:
    total_gst_collected: float
    total_gst_paid: float
    net_gst_liability: float
    compliance_score: float
    compliance_status: GSTComplianceStatus
    gst_returns_due: List[Dict[str, any]]
    gst_penalties: List[Dict[str, any]]
    gst_recommendations: List[str]

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
        
        # Amount-based features - handle None values safely
        amount_raw = invoice_data.get('amount', 0)
        features.append(float(amount_raw) if amount_raw is not None else 0.0)
        features.append(0.0)  # tax_amount not available, use 0
        
        # Time-based features - handle None values safely
        date_str = invoice_data.get('date', '')
        if date_str:
            try:
                invoice_date = datetime.fromisoformat(date_str)
                features.append(invoice_date.weekday())
                features.append(invoice_date.day)
            except (ValueError, TypeError):
                features.extend([0, 0])  # Default values if date parsing fails
        else:
            features.extend([0, 0])  # Default values if no date
        
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
        date_str = invoice_data.get('date', '')
        
        if not date_str:
            return False
            
        try:
            invoice_date = datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return False
        
        # Look for same GSTIN used on same day
        for data in historical_data:
            data_date_str = data.get('date', '')
            if not data_date_str:
                continue
            try:
                data_date = datetime.fromisoformat(data_date_str)
                if (data.get('gstin') == invoice_gstin and data_date == invoice_date):
                    return True
            except (ValueError, TypeError):
                continue
                
        return False
        
    def _check_abnormal_amount(
        self,
        invoice_data: Dict,
        historical_data: List[Dict]
    ) -> bool:
        """Check for abnormal invoice amounts"""
        amount_raw = invoice_data.get('amount', 0)
        try:
            amount = float(amount_raw) if amount_raw is not None else 0.0
        except (ValueError, TypeError):
            amount = 0.0
            
        amounts = []
        for d in historical_data:
            amount_raw = d.get('amount', 0)
            try:
                amounts.append(float(amount_raw) if amount_raw is not None else 0.0)
            except (ValueError, TypeError):
                amounts.append(0.0)
        
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
        dates = []
        for d in vendor_history:
            date_str = d.get('date', '')
            if date_str:
                try:
                    dates.append(datetime.fromisoformat(date_str))
                except (ValueError, TypeError):
                    continue
        
        if len(dates) < 2:
            return False
            
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
            date_str = data.get('date', '')
            if date_str:
                try:
                    dates.append(datetime.fromisoformat(date_str))
                except (ValueError, TypeError):
                    continue
                    
            amount_raw = data.get('amount', 0)
            try:
                amounts.append(float(amount_raw) if amount_raw is not None else 0.0)
            except (ValueError, TypeError):
                amounts.append(0.0)
            
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

    def analyze_cash_flow(self, invoices: List[Dict]) -> CashFlowAnalysis:
        """
        Analyze cash flow patterns from invoice data
        
        Args:
            invoices: List of invoice dictionaries with extracted details
            
        Returns:
            CashFlowAnalysis containing comprehensive cash flow insights
        """
        try:
            # Calculate basic cash flow metrics
            total_inflow = sum(float(inv.get('amount', 0)) for inv in invoices if inv.get('amount'))
            total_outflow = 0  # In a real system, this would be from expense invoices
            net_cash_flow = total_inflow - total_outflow
            
            # Calculate daily averages
            if invoices:
                date_range = self._calculate_date_range(invoices)
                days = max(1, (date_range['end'] - date_range['start']).days)
                average_daily_flow = net_cash_flow / days
            else:
                average_daily_flow = 0
            
            # Determine cash flow trend
            cash_flow_trend = self._determine_cash_flow_trend(invoices)
            
            # Generate monthly breakdown
            monthly_breakdown = self._generate_monthly_breakdown(invoices)
            
            # Generate cash flow forecast
            cash_flow_forecast = self._generate_cash_flow_forecast(invoices)
            
            # Identify risk factors
            risk_factors = self._identify_cash_flow_risks(invoices)
            
            return CashFlowAnalysis(
                total_inflow=total_inflow,
                total_outflow=total_outflow,
                net_cash_flow=net_cash_flow,
                average_daily_flow=average_daily_flow,
                cash_flow_trend=cash_flow_trend,
                monthly_breakdown=monthly_breakdown,
                cash_flow_forecast=cash_flow_forecast,
                risk_factors=risk_factors
            )
            
        except Exception as e:
            logger.error(f"Error in cash flow analysis: {str(e)}")
            return CashFlowAnalysis(
                total_inflow=0,
                total_outflow=0,
                net_cash_flow=0,
                average_daily_flow=0,
                cash_flow_trend="stable",
                monthly_breakdown=[],
                cash_flow_forecast=[],
                risk_factors=["Analysis failed"]
            )
    
    def analyze_gst_compliance(self, invoices: List[Dict]) -> GSTComplianceAnalysis:
        """
        Analyze GST compliance from invoice data
        
        Args:
            invoices: List of invoice dictionaries with extracted details
            
        Returns:
            GSTComplianceAnalysis containing GST compliance insights
        """
        try:
            # Calculate GST metrics
            total_gst_collected = sum(float(inv.get('gst_amount', 0)) for inv in invoices if inv.get('gst_amount'))
            total_gst_paid = 0  # In a real system, this would be from input tax credits
            net_gst_liability = total_gst_collected - total_gst_paid
            
            # Calculate compliance score
            compliance_score = self._calculate_gst_compliance_score(invoices)
            
            # Determine compliance status
            compliance_status = self._determine_gst_compliance_status(compliance_score, invoices)
            
            # Generate GST returns due
            gst_returns_due = self._generate_gst_returns_due(invoices)
            
            # Identify potential penalties
            gst_penalties = self._identify_gst_penalties(invoices)
            
            # Generate recommendations
            gst_recommendations = self._generate_gst_recommendations(invoices, compliance_score)
            
            return GSTComplianceAnalysis(
                total_gst_collected=total_gst_collected,
                total_gst_paid=total_gst_paid,
                net_gst_liability=net_gst_liability,
                compliance_score=compliance_score,
                compliance_status=compliance_status,
                gst_returns_due=gst_returns_due,
                gst_penalties=gst_penalties,
                gst_recommendations=gst_recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in GST compliance analysis: {str(e)}")
            return GSTComplianceAnalysis(
                total_gst_collected=0,
                total_gst_paid=0,
                net_gst_liability=0,
                compliance_score=0,
                compliance_status=GSTComplianceStatus.PENDING,
                gst_returns_due=[],
                gst_penalties=[],
                gst_recommendations=["Analysis failed"]
            )
    
    def _calculate_date_range(self, invoices: List[Dict]) -> Dict[str, datetime]:
        """Calculate the date range of invoices"""
        dates = []
        for inv in invoices:
            date_str = inv.get('date')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        date_obj = date_str
                    dates.append(date_obj)
                except (ValueError, TypeError):
                    continue
        
        if dates:
            return {
                'start': min(dates),
                'end': max(dates)
            }
        else:
            return {
                'start': datetime.now(),
                'end': datetime.now()
            }
    
    def _determine_cash_flow_trend(self, invoices: List[Dict]) -> str:
        """Determine if cash flow is increasing, decreasing, or stable"""
        if len(invoices) < 2:
            return "stable"
        
        try:
            # Sort invoices by date
            sorted_invoices = sorted(invoices, key=lambda x: x.get('date', ''))
            
            # Calculate monthly totals
            monthly_totals = {}
            for inv in sorted_invoices:
                date_str = inv.get('date', '')
                if date_str:
                    try:
                        if isinstance(date_str, str):
                            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:
                            date_obj = date_str
                        month_key = date_obj.strftime("%Y-%m")
                        
                        amount_raw = inv.get('amount', 0)
                        try:
                            amount = float(amount_raw) if amount_raw is not None else 0.0
                        except (ValueError, TypeError):
                            amount = 0.0
                            
                        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount
                    except (ValueError, TypeError):
                        continue
            
            if len(monthly_totals) < 2:
                return "stable"
            
            # Calculate trend
            months = sorted(monthly_totals.keys())
            first_month = monthly_totals[months[0]]
            last_month = monthly_totals[months[-1]]
            
            if last_month > first_month * 1.1:
                return "increasing"
            elif last_month < first_month * 0.9:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error in cash flow trend analysis: {str(e)}")
            return "stable"
    
    def _generate_monthly_breakdown(self, invoices: List[Dict]) -> List[Dict[str, any]]:
        """Generate monthly cash flow breakdown"""
        monthly_data = {}
        
        try:
            for inv in invoices:
                date_str = inv.get('date', '')
                if date_str:
                    try:
                        if isinstance(date_str, str):
                            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:
                            date_obj = date_str
                        month_key = date_obj.strftime("%Y-%m")
                        
                        amount_raw = inv.get('amount', 0)
                        try:
                            amount = float(amount_raw) if amount_raw is not None else 0.0
                        except (ValueError, TypeError):
                            amount = 0.0
                        
                        gst_amount_raw = inv.get('gst_amount', 0)
                        try:
                            gst_amount = float(gst_amount_raw) if gst_amount_raw is not None else 0.0
                        except (ValueError, TypeError):
                            gst_amount = 0.0
                        
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {
                                'month': month_key,
                                'total_amount': 0,
                                'invoice_count': 0,
                                'gst_collected': 0
                            }
                        
                        monthly_data[month_key]['total_amount'] += amount
                        monthly_data[month_key]['invoice_count'] += 1
                        monthly_data[month_key]['gst_collected'] += gst_amount
                        
                    except (ValueError, TypeError):
                        continue
            
            return list(monthly_data.values())
            
        except Exception as e:
            logger.error(f"Error in monthly breakdown: {str(e)}")
            return []
    
    def _generate_cash_flow_forecast(self, invoices: List[Dict]) -> List[CashFlowPrediction]:
        """Generate cash flow forecast for next 3 months"""
        if len(invoices) < 3:
            return []
        
        try:
            # Calculate average monthly cash flow
            monthly_totals = {}
            for inv in invoices:
                date_str = inv.get('date', '')
                if date_str:
                    try:
                        if isinstance(date_str, str):
                            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:
                            date_obj = date_str
                        month_key = date_obj.strftime("%Y-%m")
                        
                        amount_raw = inv.get('amount', 0)
                        try:
                            amount = float(amount_raw) if amount_raw is not None else 0.0
                        except (ValueError, TypeError):
                            amount = 0.0
                            
                        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount
                    except (ValueError, TypeError):
                        continue
            
            if not monthly_totals:
                return []
            
            avg_monthly_flow = np.mean(list(monthly_totals.values()))
            std_monthly_flow = np.std(list(monthly_totals.values()))
            
            # Generate 3-month forecast
            forecast = []
            last_date = max(datetime.fromisoformat(date.replace('Z', '+00:00')) for date in monthly_totals.keys())
            
            for i in range(1, 4):
                forecast_date = last_date + timedelta(days=30*i)
                predicted_amount = avg_monthly_flow
                confidence_interval = (
                    predicted_amount - 1.96 * std_monthly_flow,
                    predicted_amount + 1.96 * std_monthly_flow
                )
                
                forecast.append(CashFlowPrediction(
                    date=forecast_date,
                    predicted_amount=predicted_amount,
                    confidence_interval=confidence_interval,
                    contributing_factors=["Historical average", "Seasonal patterns"]
                ))
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error in cash flow forecast: {str(e)}")
            return []
    
    def _identify_cash_flow_risks(self, invoices: List[Dict]) -> List[str]:
        """Identify potential cash flow risks"""
        risks = []
        
        if not invoices:
            risks.append("No invoice data available")
            return risks
        
        try:
            # Check for late payments
            late_payments = 0
            for inv in invoices:
                # In a real system, you'd check payment dates vs due dates
                pass
            
            # Check for concentration risk
            vendor_amounts = {}
            for inv in invoices:
                vendor = inv.get('vendor', 'Unknown')
                amount_raw = inv.get('amount', 0)
                try:
                    amount = float(amount_raw) if amount_raw is not None else 0.0
                except (ValueError, TypeError):
                    amount = 0.0
                vendor_amounts[vendor] = vendor_amounts.get(vendor, 0) + amount
            
            if vendor_amounts:
                max_vendor_amount = max(vendor_amounts.values())
                total_amount = sum(vendor_amounts.values())
                if total_amount > 0 and max_vendor_amount / total_amount > 0.5:
                    risks.append("High vendor concentration risk")
            
            # Check for declining trends
            if self._determine_cash_flow_trend(invoices) == "decreasing":
                risks.append("Declining cash flow trend detected")
            
            # Check for low cash flow
            total_inflow = sum(float(inv.get('amount', 0)) for inv in invoices if inv.get('amount'))
            if total_inflow < 10000:  # Threshold for low cash flow
                risks.append("Low cash flow detected")
            
            # Check for irregular payment patterns
            if len(invoices) > 1:
                # Check if there are large gaps between invoices
                dates = []
                for inv in invoices:
                    date_str = inv.get('date', '')
                    if date_str:
                        try:
                            if isinstance(date_str, str):
                                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            else:
                                date_obj = date_str
                            dates.append(date_obj)
                        except (ValueError, TypeError):
                            continue
                
                if len(dates) > 1:
                    dates.sort()
                    gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                    avg_gap = sum(gaps) / len(gaps)
                    if avg_gap > 30:  # More than 30 days average gap
                        risks.append("Irregular payment patterns detected")
            
        except Exception as e:
            logger.error(f"Error in risk factor analysis: {str(e)}")
            risks.append("Risk analysis failed due to data issues")
        
        return risks
    
    def _calculate_gst_compliance_score(self, invoices: List[Dict]) -> float:
        """Calculate GST compliance score (0-100)"""
        if not invoices:
            return 0
        
        score = 100
        total_invoices = len(invoices)
        
        # Check for missing GSTIN
        missing_gstin = sum(1 for inv in invoices if not inv.get('gstin'))
        if missing_gstin > 0:
            score -= (missing_gstin / total_invoices) * 30
        
        # Check for missing HSN codes
        missing_hsn = sum(1 for inv in invoices if not inv.get('hsn_code'))
        if missing_hsn > 0:
            score -= (missing_hsn / total_invoices) * 20
        
        # Check for missing GST amounts
        missing_gst = sum(1 for inv in invoices if not inv.get('gst_amount'))
        if missing_gst > 0:
            score -= (missing_gst / total_invoices) * 25
        
        return max(0, score)
    
    def _determine_gst_compliance_status(self, compliance_score: float, invoices: List[Dict]) -> GSTComplianceStatus:
        """Determine GST compliance status based on score and data"""
        if compliance_score >= 90:
            return GSTComplianceStatus.COMPLIANT
        elif compliance_score >= 70:
            return GSTComplianceStatus.WARNING
        elif compliance_score >= 50:
            return GSTComplianceStatus.NON_COMPLIANT
        else:
            return GSTComplianceStatus.PENDING
    
    def _generate_gst_returns_due(self, invoices: List[Dict]) -> List[Dict[str, any]]:
        """Generate list of GST returns due"""
        returns_due = []
        
        # In a real system, this would check actual GST return filing dates
        # For now, we'll generate mock data based on invoice dates
        monthly_gst = {}
        for inv in invoices:
            date_str = inv.get('date', '')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        date_obj = date_str
                    month_key = date_obj.strftime("%Y-%m")
                    gst_amount = float(inv.get('gst_amount', 0))
                    monthly_gst[month_key] = monthly_gst.get(month_key, 0) + gst_amount
                except (ValueError, TypeError):
                    continue
        
        for month, gst_amount in monthly_gst.items():
            returns_due.append({
                'period': month,
                'gst_amount': gst_amount,
                'due_date': f"{month}-20",  # Mock due date
                'status': 'pending'
            })
        
        return returns_due
    
    def _identify_gst_penalties(self, invoices: List[Dict]) -> List[Dict[str, any]]:
        """Identify potential GST penalties"""
        penalties = []
        
        # Check for late filing (mock implementation)
        for inv in invoices:
            date_str = inv.get('date', '')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        date_obj = date_str
                    
                    # Mock penalty check - if invoice is older than 30 days without GST filing
                    if (datetime.now() - date_obj).days > 30:
                        penalties.append({
                            'type': 'Late GST Filing',
                            'amount': 1000,  # Mock penalty amount
                            'description': f'GST return for {date_obj.strftime("%Y-%m")} is overdue',
                            'severity': 'medium'
                        })
                except (ValueError, TypeError):
                    continue
        
        return penalties
    
    def _generate_gst_recommendations(self, invoices: List[Dict], compliance_score: float) -> List[str]:
        """Generate GST compliance recommendations"""
        recommendations = []
        
        if compliance_score < 90:
            recommendations.append("Improve GSTIN collection from vendors")
        
        if compliance_score < 80:
            recommendations.append("Ensure HSN codes are captured for all invoices")
        
        if compliance_score < 70:
            recommendations.append("Verify GST amounts are correctly calculated")
        
        # Check for specific issues
        missing_gstin_count = sum(1 for inv in invoices if not inv.get('gstin'))
        if missing_gstin_count > 0:
            recommendations.append(f"Collect GSTIN from {missing_gstin_count} vendors")
        
        missing_hsn_count = sum(1 for inv in invoices if not inv.get('hsn_code'))
        if missing_hsn_count > 0:
            recommendations.append(f"Add HSN codes to {missing_hsn_count} invoices")
        
        return recommendations 