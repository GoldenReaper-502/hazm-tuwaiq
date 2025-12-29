"""
HAZM TUWAIQ - Trend Analyzer
Pattern detection and trend analysis from historical safety data
"""

import logging
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from .models import TrendAnalysis, TrendDirection, TimeFrame


class TrendAnalyzer:
    """
    محلل الاتجاهات
    Detect patterns and trends in safety metrics
    """
    
    def __init__(self):
        """Initialize trend analyzer"""
        self.logger = logging.getLogger(__name__)
        
        # Metric history
        self.metrics_history: Dict[str, List[Dict]] = defaultdict(list)
    
    def analyze_trend(
        self,
        metric: str,
        target: str,
        organization_id: str,
        time_frame: TimeFrame = TimeFrame.DAILY,
        days_back: int = 30,
        data_points: Optional[List[Dict[str, Any]]] = None
    ) -> TrendAnalysis:
        """
        Analyze trend for specific metric
        
        Args:
            metric: Metric name (e.g., "incident_rate")
            target: Target entity (zone, site, org)
            organization_id: Organization ID
            time_frame: Time aggregation frame
            days_back: Number of days to analyze
            data_points: Historical data points
            
        Returns:
            TrendAnalysis object with complete trend information
        """
        try:
            # Get or simulate data points
            if data_points is None:
                data_points = self._simulate_data_points(metric, days_back, time_frame)
            
            # Extract values and timestamps
            values = [dp['value'] for dp in data_points]
            timestamps = [dp['timestamp'] for dp in data_points]
            
            if len(values) < 2:
                raise ValueError("Insufficient data points for trend analysis")
            
            # Calculate statistical measures
            mean_val = statistics.mean(values)
            median_val = statistics.median(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            min_val = min(values)
            max_val = max(values)
            
            # Calculate trend direction and slope
            direction, slope, change_pct = self._calculate_trend_direction(values)
            
            # Detect patterns
            patterns = self._detect_patterns(values, timestamps, time_frame)
            
            # Detect seasonality
            seasonality = self._detect_seasonality(values, timestamps, time_frame)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(data_points, mean_val, std_dev)
            
            # Generate insights
            insights = self._generate_insights(
                metric, direction, change_pct, patterns, anomalies
            )
            
            # Generate summary
            summary = self._generate_summary(
                metric, direction, change_pct, mean_val, patterns
            )
            
            # Create analysis
            analysis = TrendAnalysis(
                metric=metric,
                metric_ar=self._translate_metric(metric),
                target=target,
                time_frame=time_frame,
                start_date=timestamps[0] if timestamps else datetime.now() - timedelta(days=days_back),
                end_date=timestamps[-1] if timestamps else datetime.now(),
                data_points=len(data_points),
                direction=direction,
                change_percentage=round(change_pct, 2),
                slope=round(slope, 4),
                mean=round(mean_val, 2),
                median=round(median_val, 2),
                std_deviation=round(std_dev, 2),
                min_value=round(min_val, 2),
                max_value=round(max_val, 2),
                patterns_detected=patterns,
                seasonality=seasonality,
                anomalies=anomalies,
                time_series=data_points,
                summary=summary,
                summary_ar=self._translate_summary(summary),
                insights=insights,
                organization_id=organization_id
            )
            
            self.logger.info(
                f"Trend analysis completed: {metric} - {direction.value} ({change_pct:+.1f}%)"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze trend: {e}")
            raise
    
    def _calculate_trend_direction(
        self,
        values: List[float]
    ) -> Tuple[TrendDirection, float, float]:
        """Calculate trend direction, slope, and change percentage"""
        if len(values) < 2:
            return TrendDirection.STABLE, 0.0, 0.0
        
        # Linear regression
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]
        
        # Calculate change percentage
        first_val = values[0] if values[0] != 0 else 0.01
        last_val = values[-1]
        change_pct = ((last_val - first_val) / first_val) * 100
        
        # Determine direction
        if abs(change_pct) < 5:
            direction = TrendDirection.STABLE
        elif change_pct > 15:
            direction = TrendDirection.DEGRADING if slope > 0 else TrendDirection.IMPROVING
        elif change_pct < -15:
            direction = TrendDirection.IMPROVING if slope < 0 else TrendDirection.DEGRADING
        else:
            # Check volatility
            volatility = np.std(y) / np.mean(y) if np.mean(y) != 0 else 0
            if volatility > 0.3:
                direction = TrendDirection.VOLATILE
            else:
                direction = TrendDirection.STABLE
        
        # For incident metrics, increasing is degrading
        if change_pct > 5 and slope > 0:
            direction = TrendDirection.DEGRADING
        elif change_pct < -5 and slope < 0:
            direction = TrendDirection.IMPROVING
        
        return direction, slope, change_pct
    
    def _detect_patterns(
        self,
        values: List[float],
        timestamps: List[datetime],
        time_frame: TimeFrame
    ) -> List[str]:
        """Detect temporal patterns in data"""
        patterns = []
        
        if len(values) < 7:
            return patterns
        
        # Weekly pattern (if daily data)
        if time_frame == TimeFrame.DAILY and len(values) >= 14:
            # Group by day of week
            by_weekday = defaultdict(list)
            for i, ts in enumerate(timestamps):
                by_weekday[ts.weekday()].append(values[i])
            
            # Find peak day
            avg_by_day = {day: np.mean(vals) for day, vals in by_weekday.items()}
            if avg_by_day:
                peak_day = max(avg_by_day, key=avg_by_day.get)
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                patterns.append(f"weekly_peak_{days[peak_day].lower()}")
        
        # Time of day pattern (if hourly data)
        if time_frame == TimeFrame.HOURLY and len(timestamps) >= 24:
            by_hour = defaultdict(list)
            for i, ts in enumerate(timestamps):
                by_hour[ts.hour].append(values[i])
            
            avg_by_hour = {hour: np.mean(vals) for hour, vals in by_hour.items()}
            if avg_by_hour:
                peak_hour = max(avg_by_hour, key=avg_by_hour.get)
                if 6 <= peak_hour <= 12:
                    patterns.append("morning_peak")
                elif 13 <= peak_hour <= 17:
                    patterns.append("afternoon_peak")
                elif 18 <= peak_hour <= 22:
                    patterns.append("evening_peak")
        
        # Spike detection
        threshold = np.mean(values) + 2 * np.std(values)
        spikes = [v for v in values if v > threshold]
        if len(spikes) >= 2:
            patterns.append("recurring_spikes")
        
        # Cyclical pattern
        if len(values) >= 30:
            # Simple autocorrelation check
            mean = np.mean(values)
            deviations = [v - mean for v in values]
            
            # Check for 7-day cycle
            if len(deviations) >= 14:
                correlation_7d = np.corrcoef(deviations[:7], deviations[7:14])[0, 1]
                if correlation_7d > 0.7:
                    patterns.append("weekly_cycle")
        
        return patterns
    
    def _detect_seasonality(
        self,
        values: List[float],
        timestamps: List[datetime],
        time_frame: TimeFrame
    ) -> Optional[Dict[str, Any]]:
        """Detect seasonal patterns"""
        if len(values) < 14:
            return None
        
        seasonality = {}
        
        # Weekly seasonality
        if time_frame == TimeFrame.DAILY and len(values) >= 14:
            by_weekday = defaultdict(list)
            for i, ts in enumerate(timestamps):
                by_weekday[ts.weekday()].append(values[i])
            
            if len(by_weekday) >= 5:
                avg_by_day = {day: np.mean(vals) for day, vals in by_weekday.items()}
                peak_day = max(avg_by_day, key=avg_by_day.get)
                min_day = min(avg_by_day, key=avg_by_day.get)
                
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                seasonality = {
                    'pattern': 'weekly',
                    'peak_day': days[peak_day],
                    'low_day': days[min_day],
                    'strength': round((avg_by_day[peak_day] - avg_by_day[min_day]) / avg_by_day[min_day], 2)
                }
        
        return seasonality if seasonality else None
    
    def _detect_anomalies(
        self,
        data_points: List[Dict[str, Any]],
        mean: float,
        std_dev: float
    ) -> List[Dict[str, Any]]:
        """Detect statistical anomalies"""
        anomalies = []
        
        # Use 2-sigma threshold
        threshold = 2.0
        
        for dp in data_points:
            value = dp['value']
            deviation = abs(value - mean) / std_dev if std_dev > 0 else 0
            
            if deviation > threshold:
                anomalies.append({
                    'timestamp': dp['timestamp'].isoformat() if isinstance(dp['timestamp'], datetime) else dp['timestamp'],
                    'value': round(value, 2),
                    'expected': round(mean, 2),
                    'deviation_sigma': round(deviation, 2),
                    'type': 'spike' if value > mean else 'drop'
                })
        
        return anomalies[:10]  # Limit to top 10
    
    def _generate_insights(
        self,
        metric: str,
        direction: TrendDirection,
        change_pct: float,
        patterns: List[str],
        anomalies: List[Dict]
    ) -> List[str]:
        """Generate human-readable insights"""
        insights = []
        
        # Trend insight
        if direction == TrendDirection.DEGRADING:
            insights.append(
                f"⚠️ {metric} is increasing by {abs(change_pct):.1f}% - requires attention"
            )
        elif direction == TrendDirection.IMPROVING:
            insights.append(
                f"✅ {metric} is decreasing by {abs(change_pct):.1f}% - positive trend"
            )
        elif direction == TrendDirection.VOLATILE:
            insights.append(
                f"📊 {metric} shows high volatility - inconsistent safety performance"
            )
        
        # Pattern insights
        if "weekly_peak_monday" in patterns:
            insights.append("📅 Monday shows highest incident rate - consider additional briefings")
        if "morning_peak" in patterns:
            insights.append("🌅 Morning shift has elevated risk - increase supervision")
        if "recurring_spikes" in patterns:
            insights.append("📈 Recurring spikes detected - investigate root causes")
        
        # Anomaly insights
        if len(anomalies) > 3:
            insights.append(f"🔍 {len(anomalies)} statistical anomalies detected - review specific dates")
        
        return insights
    
    def _generate_summary(
        self,
        metric: str,
        direction: TrendDirection,
        change_pct: float,
        mean: float,
        patterns: List[str]
    ) -> str:
        """Generate trend summary"""
        direction_text = {
            TrendDirection.IMPROVING: "improving",
            TrendDirection.DEGRADING: "degrading",
            TrendDirection.STABLE: "stable",
            TrendDirection.VOLATILE: "volatile"
        }
        
        summary = (
            f"{metric} trend is {direction_text[direction]} "
            f"with {abs(change_pct):.1f}% change. "
            f"Average value: {mean:.2f}. "
        )
        
        if patterns:
            summary += f"Detected patterns: {', '.join(patterns[:3])}."
        
        return summary
    
    def _translate_metric(self, metric: str) -> str:
        """Translate metric name to Arabic"""
        translations = {
            'incident_rate': 'معدل الحوادث',
            'near_miss_count': 'عدد شبه الحوادث',
            'compliance_score': 'مؤشر الامتثال',
            'alert_frequency': 'تكرار التنبيهات',
            'fatigue_level': 'مستوى الإرهاق',
            'ppe_compliance': 'الالتزام بمعدات السلامة'
        }
        return translations.get(metric, metric)
    
    def _translate_summary(self, summary: str) -> str:
        """Translate summary to Arabic (simplified)"""
        # In production, use proper translation service
        if "improving" in summary:
            return "الاتجاه يتحسن"
        elif "degrading" in summary:
            return "الاتجاه يتدهور"
        else:
            return "الاتجاه مستقر"
    
    def _simulate_data_points(
        self,
        metric: str,
        days: int,
        time_frame: TimeFrame
    ) -> List[Dict[str, Any]]:
        """Simulate data points for demonstration"""
        data_points = []
        
        # Base value depends on metric
        base_value = {
            'incident_rate': 5,
            'near_miss_count': 12,
            'compliance_score': 85,
            'alert_frequency': 20
        }.get(metric, 10)
        
        # Generate synthetic data
        np.random.seed(42)
        
        if time_frame == TimeFrame.DAILY:
            for i in range(days):
                timestamp = datetime.now() - timedelta(days=days-i)
                
                # Add trend
                trend = i * 0.1
                
                # Add weekly pattern
                weekly_effect = 5 * np.sin(2 * np.pi * i / 7)
                
                # Add noise
                noise = np.random.normal(0, 2)
                
                value = max(0, base_value + trend + weekly_effect + noise)
                
                data_points.append({
                    'timestamp': timestamp,
                    'value': round(value, 2)
                })
        
        elif time_frame == TimeFrame.WEEKLY:
            for i in range(min(days // 7, 12)):
                timestamp = datetime.now() - timedelta(weeks=12-i)
                value = base_value + np.random.normal(0, 3)
                data_points.append({
                    'timestamp': timestamp,
                    'value': round(max(0, value), 2)
                })
        
        return data_points
    
    def compare_trends(
        self,
        analyses: List[TrendAnalysis]
    ) -> Dict[str, Any]:
        """Compare multiple trend analyses"""
        if not analyses:
            return {}
        
        comparison = {
            'total_analyzed': len(analyses),
            'improving': len([a for a in analyses if a.direction == TrendDirection.IMPROVING]),
            'degrading': len([a for a in analyses if a.direction == TrendDirection.DEGRADING]),
            'stable': len([a for a in analyses if a.direction == TrendDirection.STABLE]),
            'avg_change': round(sum(a.change_percentage for a in analyses) / len(analyses), 2),
            'metrics': [
                {
                    'metric': a.metric,
                    'direction': a.direction.value,
                    'change': a.change_percentage
                }
                for a in analyses
            ]
        }
        
        return comparison


# Singleton instance
_trend_analyzer: Optional[TrendAnalyzer] = None


def get_trend_analyzer() -> TrendAnalyzer:
    """Get singleton TrendAnalyzer instance"""
    global _trend_analyzer
    
    if _trend_analyzer is None:
        _trend_analyzer = TrendAnalyzer()
    
    return _trend_analyzer
