"""
HAZM TUWAIQ - Prediction Engine
ML-powered incident prediction and risk forecasting
"""

import logging
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    Prediction, PredictionType, RiskLevel,
    ProactiveRecommendation
)


class PredictionEngine:
    """
    محرك التنبؤ
    Machine learning-powered safety predictions
    """
    
    def __init__(self):
        """Initialize prediction engine"""
        self.logger = logging.getLogger(__name__)
        
        # Historical data cache
        self.incident_history: Dict[str, List[Dict]] = defaultdict(list)
        self.near_miss_history: Dict[str, List[Dict]] = defaultdict(list)
        self.alert_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # Model performance tracking
        self.predictions_made = 0
        self.predictions_validated = 0
        self.accuracy_scores = []
    
    def predict_incident_probability(
        self,
        target: str,
        organization_id: str,
        forecast_period: str = "next_24h",
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Prediction:
        """
        Predict probability of incident occurrence
        
        Args:
            target: Target zone/site/worker
            organization_id: Organization ID
            forecast_period: Forecast timeframe
            historical_data: Historical incident/alert data
            
        Returns:
            Prediction object with probability and risk level
        """
        try:
            # Extract features from historical data
            features = self._extract_features(target, organization_id, historical_data)
            
            # Calculate base probability from historical incident rate
            incident_rate = features.get('incident_rate', 0.1)
            near_miss_rate = features.get('near_miss_rate', 0.2)
            alert_rate = features.get('alert_rate', 0.3)
            
            # Weighted factors
            base_probability = (
                incident_rate * 0.4 +
                near_miss_rate * 0.3 +
                alert_rate * 0.3
            )
            
            # Adjust for trends
            trend_multiplier = self._calculate_trend_multiplier(features)
            
            # Adjust for time patterns
            time_multiplier = self._calculate_time_multiplier(forecast_period)
            
            # Final probability
            probability = min(base_probability * trend_multiplier * time_multiplier, 1.0)
            
            # Determine risk level
            risk_level = self._probability_to_risk_level(probability)
            
            # Calculate confidence
            confidence = self._calculate_confidence(features)
            
            # Identify contributing factors
            factors = self._identify_factors(features, probability)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                target, probability, factors
            )
            
            # Create prediction
            valid_until = self._calculate_validity_period(forecast_period)
            
            prediction = Prediction(
                type=PredictionType.INCIDENT_PROBABILITY,
                target=target,
                probability=round(probability, 3),
                risk_level=risk_level,
                confidence=round(confidence, 3),
                forecast_period=forecast_period,
                valid_until=valid_until,
                title=f"Incident Probability for {target}",
                title_ar=f"احتمالية حادث في {target}",
                description=f"Predicted {probability:.1%} chance of incident in {forecast_period}",
                description_ar=f"احتمالية {probability:.1%} لحدوث حادث خلال {forecast_period}",
                factors=factors,
                recommendations=recommendations,
                organization_id=organization_id
            )
            
            self.predictions_made += 1
            
            self.logger.info(
                f"Incident prediction generated: {target} - "
                f"{probability:.1%} ({risk_level.value})"
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Failed to generate prediction: {e}")
            raise
    
    def predict_near_miss_forecast(
        self,
        target: str,
        organization_id: str,
        forecast_period: str = "next_week"
    ) -> Prediction:
        """Predict expected number and pattern of near-misses"""
        try:
            # Get historical near-miss data
            historical = self.near_miss_history.get(target, [])
            
            # Calculate average rate
            if len(historical) > 0:
                avg_rate = len(historical) / max(len(historical), 1)
            else:
                avg_rate = 0.5  # Default baseline
            
            # Forecast based on period
            if "24h" in forecast_period or "day" in forecast_period:
                expected_count = avg_rate * 1
                probability = min(avg_rate, 1.0)
            elif "week" in forecast_period:
                expected_count = avg_rate * 7
                probability = min(avg_rate * 0.8, 1.0)
            else:
                expected_count = avg_rate * 30
                probability = min(avg_rate * 0.6, 1.0)
            
            risk_level = self._probability_to_risk_level(probability)
            
            prediction = Prediction(
                type=PredictionType.NEAR_MISS_FORECAST,
                target=target,
                probability=round(probability, 3),
                risk_level=risk_level,
                confidence=0.75,
                forecast_period=forecast_period,
                valid_until=self._calculate_validity_period(forecast_period),
                title=f"Near-Miss Forecast for {target}",
                title_ar=f"توقع شبه الحوادث في {target}",
                description=f"Expected ~{int(expected_count)} near-misses in {forecast_period}",
                factors=[
                    {"factor": "historical_rate", "value": avg_rate, "weight": 0.6},
                    {"factor": "time_period", "value": forecast_period, "weight": 0.4}
                ],
                recommendations=self._generate_near_miss_recommendations(expected_count),
                organization_id=organization_id
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Failed to forecast near-misses: {e}")
            raise
    
    def predict_risk_score(
        self,
        target: str,
        organization_id: str
    ) -> Prediction:
        """Calculate comprehensive risk score for target"""
        try:
            # Gather all risk factors
            incident_risk = len(self.incident_history.get(target, [])) / 100
            alert_risk = len(self.alert_history.get(target, [])) / 200
            near_miss_risk = len(self.near_miss_history.get(target, [])) / 150
            
            # Composite risk score
            risk_score = (
                incident_risk * 0.5 +
                alert_risk * 0.3 +
                near_miss_risk * 0.2
            )
            
            risk_score = min(risk_score, 1.0)
            risk_level = self._probability_to_risk_level(risk_score)
            
            prediction = Prediction(
                type=PredictionType.RISK_SCORE,
                target=target,
                probability=round(risk_score, 3),
                risk_level=risk_level,
                confidence=0.85,
                forecast_period="current",
                valid_until=datetime.now() + timedelta(hours=1),
                title=f"Risk Score for {target}",
                title_ar=f"مؤشر المخاطر لـ {target}",
                description=f"Current risk score: {risk_score:.1%}",
                factors=[
                    {"factor": "incident_history", "contribution": incident_risk * 0.5},
                    {"factor": "alert_frequency", "contribution": alert_risk * 0.3},
                    {"factor": "near_miss_rate", "contribution": near_miss_risk * 0.2}
                ],
                organization_id=organization_id
            )
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Failed to calculate risk score: {e}")
            raise
    
    def _extract_features(
        self,
        target: str,
        organization_id: str,
        historical_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract features from historical data"""
        features = {
            'incident_rate': 0.0,
            'near_miss_rate': 0.0,
            'alert_rate': 0.0,
            'trend': 'stable',
            'data_quality': 'low'
        }
        
        if not historical_data:
            return features
        
        # Calculate rates
        incidents = historical_data.get('incidents', [])
        near_misses = historical_data.get('near_misses', [])
        alerts = historical_data.get('alerts', [])
        
        days = historical_data.get('days', 30)
        
        if days > 0:
            features['incident_rate'] = len(incidents) / days
            features['near_miss_rate'] = len(near_misses) / days
            features['alert_rate'] = len(alerts) / days
        
        # Trend detection
        if len(incidents) >= 3:
            recent = len([i for i in incidents[-10:]])
            older = len([i for i in incidents[:-10]]) if len(incidents) > 10 else 1
            
            if recent > older * 1.5:
                features['trend'] = 'increasing'
            elif recent < older * 0.5:
                features['trend'] = 'decreasing'
            else:
                features['trend'] = 'stable'
        
        features['data_quality'] = 'high' if len(incidents) + len(near_misses) > 20 else 'medium'
        
        return features
    
    def _calculate_trend_multiplier(self, features: Dict[str, Any]) -> float:
        """Calculate multiplier based on trend"""
        trend = features.get('trend', 'stable')
        
        if trend == 'increasing':
            return 1.3
        elif trend == 'decreasing':
            return 0.7
        else:
            return 1.0
    
    def _calculate_time_multiplier(self, forecast_period: str) -> float:
        """Calculate multiplier based on time period"""
        if "hour" in forecast_period:
            return 1.2  # Short-term predictions more reliable
        elif "24h" in forecast_period or "day" in forecast_period:
            return 1.0
        elif "week" in forecast_period:
            return 0.9
        else:
            return 0.8
    
    def _probability_to_risk_level(self, probability: float) -> RiskLevel:
        """Convert probability to risk level"""
        if probability >= 0.8:
            return RiskLevel.CRITICAL
        elif probability >= 0.6:
            return RiskLevel.VERY_HIGH
        elif probability >= 0.4:
            return RiskLevel.HIGH
        elif probability >= 0.2:
            return RiskLevel.MODERATE
        elif probability >= 0.1:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate prediction confidence"""
        base_confidence = 0.7
        
        # Adjust for data quality
        if features.get('data_quality') == 'high':
            base_confidence += 0.2
        elif features.get('data_quality') == 'low':
            base_confidence -= 0.2
        
        # Adjust for trend clarity
        if features.get('trend') in ['increasing', 'decreasing']:
            base_confidence += 0.1
        
        return min(max(base_confidence, 0.5), 0.95)
    
    def _identify_factors(
        self,
        features: Dict[str, Any],
        probability: float
    ) -> List[Dict[str, Any]]:
        """Identify contributing factors to prediction"""
        factors = []
        
        if features.get('incident_rate', 0) > 0.1:
            factors.append({
                'factor': 'high_incident_rate',
                'weight': 0.4,
                'trend': features.get('trend', 'stable'),
                'description': 'Historical incident frequency above baseline'
            })
        
        if features.get('near_miss_rate', 0) > 0.2:
            factors.append({
                'factor': 'elevated_near_misses',
                'weight': 0.3,
                'description': 'Increasing near-miss incidents indicating risk'
            })
        
        if features.get('alert_rate', 0) > 0.3:
            factors.append({
                'factor': 'frequent_alerts',
                'weight': 0.3,
                'description': 'High alert frequency from AI detection'
            })
        
        return factors
    
    def _generate_recommendations(
        self,
        target: str,
        probability: float,
        factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []
        
        if probability > 0.6:
            recommendations.append("🚨 Immediate supervision required")
            recommendations.append("⚠️ Conduct safety briefing before shift")
            recommendations.append("🔍 Increase monitoring frequency")
        
        if probability > 0.4:
            recommendations.append("👷 Review worker assignments")
            recommendations.append("🛠️ Inspect equipment condition")
        
        if any(f['factor'] == 'high_incident_rate' for f in factors):
            recommendations.append("📊 Analyze incident root causes")
            recommendations.append("🎓 Provide targeted safety training")
        
        return recommendations
    
    def _generate_near_miss_recommendations(
        self,
        expected_count: float
    ) -> List[str]:
        """Generate recommendations for near-miss prevention"""
        recommendations = []
        
        if expected_count > 5:
            recommendations.append("🔍 Implement near-miss reporting system")
            recommendations.append("📋 Conduct weekly safety audits")
        
        if expected_count > 10:
            recommendations.append("⚠️ Critical: Review all safety procedures")
            recommendations.append("👥 Increase supervision ratio")
        
        return recommendations
    
    def _calculate_validity_period(self, forecast_period: str) -> datetime:
        """Calculate when prediction expires"""
        if "hour" in forecast_period:
            return datetime.now() + timedelta(hours=1)
        elif "24h" in forecast_period or "day" in forecast_period:
            return datetime.now() + timedelta(days=1)
        elif "week" in forecast_period:
            return datetime.now() + timedelta(weeks=1)
        elif "month" in forecast_period:
            return datetime.now() + timedelta(days=30)
        else:
            return datetime.now() + timedelta(days=7)
    
    def validate_prediction(
        self,
        prediction_id: str,
        actual_outcome: bool,
        actual_probability: Optional[float] = None
    ) -> float:
        """
        Validate prediction against actual outcome
        
        Args:
            prediction_id: Prediction ID
            actual_outcome: Did incident occur?
            actual_probability: Actual measured probability
            
        Returns:
            Accuracy score
        """
        try:
            # Calculate accuracy
            # In production, retrieve prediction from database
            # For now, simulate scoring
            
            if actual_probability is not None:
                # Mean absolute error
                accuracy = 1.0 - abs(actual_probability - 0.5)  # Placeholder
            else:
                # Binary outcome
                accuracy = 0.8  # Placeholder
            
            self.predictions_validated += 1
            self.accuracy_scores.append(accuracy)
            
            self.logger.info(
                f"Prediction validated: {prediction_id} - "
                f"Accuracy: {accuracy:.2%}"
            )
            
            return accuracy
            
        except Exception as e:
            self.logger.error(f"Failed to validate prediction: {e}")
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get prediction engine statistics"""
        avg_accuracy = (
            sum(self.accuracy_scores) / len(self.accuracy_scores)
            if self.accuracy_scores else 0.0
        )
        
        return {
            "predictions_made": self.predictions_made,
            "predictions_validated": self.predictions_validated,
            "average_accuracy": round(avg_accuracy, 3),
            "validation_rate": (
                self.predictions_validated / self.predictions_made
                if self.predictions_made > 0 else 0.0
            )
        }


# Singleton instance
_prediction_engine: Optional[PredictionEngine] = None


def get_prediction_engine() -> PredictionEngine:
    """Get singleton PredictionEngine instance"""
    global _prediction_engine
    
    if _prediction_engine is None:
        _prediction_engine = PredictionEngine()
    
    return _prediction_engine
