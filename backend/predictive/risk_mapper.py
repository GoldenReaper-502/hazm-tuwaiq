"""
HAZM TUWAIQ - Risk Mapper
Generate spatial risk heatmaps and identify high-risk zones
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from .models import RiskHeatmap, RiskLevel


class RiskMapper:
    """
    مخطط المخاطر
    Generate and analyze spatial risk distributions
    """
    
    def __init__(self):
        """Initialize risk mapper"""
        self.logger = logging.getLogger(__name__)
        
        # Heatmap cache
        self.heatmaps: Dict[str, RiskHeatmap] = {}
        
        # Risk data by zone
        self.zone_data: Dict[str, Dict[str, List]] = defaultdict(lambda: defaultdict(list))
    
    def generate_heatmap(
        self,
        site_id: str,
        organization_id: str,
        time_period: str = "last_7_days",
        min_risk_threshold: Optional[float] = None,
        zone_data: Optional[List[Dict[str, Any]]] = None
    ) -> RiskHeatmap:
        """
        Generate risk heatmap for site
        
        Args:
            site_id: Site ID
            organization_id: Organization ID
            time_period: Time period for analysis
            min_risk_threshold: Minimum risk to include
            zone_data: Optional zone risk data
            
        Returns:
            RiskHeatmap with spatial risk distribution
        """
        try:
            # Get or simulate zone data
            if zone_data is None:
                zone_data = self._simulate_zone_data(site_id)
            
            # Calculate risk scores for each zone
            zones_with_risk = []
            
            for zone in zone_data:
                risk_score = self._calculate_zone_risk(zone)
                
                # Apply threshold filter
                if min_risk_threshold and risk_score < min_risk_threshold:
                    continue
                
                risk_level = self._score_to_risk_level(risk_score)
                
                zone_info = {
                    'zone_id': zone.get('zone_id', 'ZONE-???'),
                    'zone_name': zone.get('zone_name', 'Unknown Zone'),
                    'zone_name_ar': zone.get('zone_name_ar'),
                    'risk_score': round(risk_score, 3),
                    'risk_level': risk_level.value,
                    'incident_count': zone.get('incident_count', 0),
                    'near_miss_count': zone.get('near_miss_count', 0),
                    'alert_count': zone.get('alert_count', 0),
                    'worker_count': zone.get('worker_count', 0),
                    'equipment_count': zone.get('equipment_count', 0),
                    'coordinates': zone.get('coordinates', {'x': 0, 'y': 0, 'radius': 50})
                }
                
                zones_with_risk.append(zone_info)
            
            # Sort by risk score
            zones_with_risk.sort(key=lambda z: z['risk_score'], reverse=True)
            
            # Identify hot spots (top 20% highest risk)
            hot_spot_count = max(1, len(zones_with_risk) // 5)
            hot_spots = zones_with_risk[:hot_spot_count]
            
            # Calculate aggregate statistics
            total_zones = len(zones_with_risk)
            highest_risk = zones_with_risk[0]['zone_id'] if zones_with_risk else "N/A"
            lowest_risk = zones_with_risk[-1]['zone_id'] if zones_with_risk else "N/A"
            avg_risk = (
                sum(z['risk_score'] for z in zones_with_risk) / total_zones
                if total_zones > 0 else 0.0
            )
            
            # Risk distribution
            risk_distribution = defaultdict(int)
            for zone in zones_with_risk:
                risk_distribution[zone['risk_level']] += 1
            
            # Create heatmap
            heatmap = RiskHeatmap(
                site_id=site_id,
                time_period=time_period,
                zones=zones_with_risk,
                total_zones=total_zones,
                highest_risk_zone=highest_risk,
                lowest_risk_zone=lowest_risk,
                average_risk_score=round(avg_risk, 3),
                risk_distribution=dict(risk_distribution),
                hot_spots=[
                    {
                        'zone_id': hs['zone_id'],
                        'zone_name': hs['zone_name'],
                        'risk_score': hs['risk_score'],
                        'incidents': hs['incident_count'],
                        'priority': i + 1
                    }
                    for i, hs in enumerate(hot_spots)
                ],
                organization_id=organization_id
            )
            
            # Cache heatmap
            self.heatmaps[heatmap.id] = heatmap
            
            self.logger.info(
                f"Risk heatmap generated: {site_id} - "
                f"{total_zones} zones, avg risk: {avg_risk:.2f}"
            )
            
            return heatmap
            
        except Exception as e:
            self.logger.error(f"Failed to generate heatmap: {e}")
            raise
    
    def _calculate_zone_risk(self, zone: Dict[str, Any]) -> float:
        """Calculate composite risk score for zone"""
        # Base risk from incidents
        incident_risk = zone.get('incident_count', 0) * 0.4
        
        # Near-miss risk
        near_miss_risk = zone.get('near_miss_count', 0) * 0.2
        
        # Alert risk
        alert_risk = zone.get('alert_count', 0) * 0.1
        
        # Occupancy risk (more workers = higher exposure)
        worker_count = zone.get('worker_count', 0)
        occupancy_risk = min(worker_count / 10, 1.0) * 0.2
        
        # Equipment risk
        equipment_count = zone.get('equipment_count', 0)
        equipment_risk = min(equipment_count / 5, 1.0) * 0.1
        
        # Composite score
        total_risk = (
            incident_risk +
            near_miss_risk +
            alert_risk +
            occupancy_risk +
            equipment_risk
        )
        
        # Normalize to 0-1
        return min(total_risk, 1.0)
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to level"""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.VERY_HIGH
        elif score >= 0.4:
            return RiskLevel.HIGH
        elif score >= 0.2:
            return RiskLevel.MODERATE
        elif score >= 0.1:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def _simulate_zone_data(self, site_id: str) -> List[Dict[str, Any]]:
        """Simulate zone data for demonstration"""
        import random
        random.seed(42)
        
        zones = []
        zone_names = [
            ('Welding Area', 'منطقة اللحام'),
            ('Assembly Line', 'خط التجميع'),
            ('Storage Warehouse', 'مستودع التخزين'),
            ('Machine Shop', 'ورشة الآلات'),
            ('Loading Dock', 'منصة التحميل'),
            ('Paint Shop', 'ورشة الدهان'),
            ('Quality Control', 'مراقبة الجودة'),
            ('Maintenance Bay', 'منطقة الصيانة')
        ]
        
        for i, (name, name_ar) in enumerate(zone_names):
            zones.append({
                'zone_id': f"ZONE-{i+1:03d}",
                'zone_name': name,
                'zone_name_ar': name_ar,
                'incident_count': random.randint(0, 5),
                'near_miss_count': random.randint(0, 15),
                'alert_count': random.randint(5, 30),
                'worker_count': random.randint(5, 25),
                'equipment_count': random.randint(2, 10),
                'coordinates': {
                    'x': random.randint(50, 450),
                    'y': random.randint(50, 350),
                    'radius': random.randint(30, 60)
                }
            })
        
        return zones
    
    def get_zone_risk_history(
        self,
        zone_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get historical risk scores for zone"""
        history = self.zone_data.get(zone_id, {}).get('history', [])
        
        # Filter by date range
        cutoff = datetime.now() - timedelta(days=days)
        history = [h for h in history if h['timestamp'] >= cutoff]
        
        return history
    
    def identify_high_risk_patterns(
        self,
        heatmap: RiskHeatmap
    ) -> List[Dict[str, Any]]:
        """Identify patterns in high-risk zones"""
        patterns = []
        
        # Pattern 1: Adjacent high-risk zones
        high_risk_zones = [
            z for z in heatmap.zones
            if z['risk_level'] in ['high', 'very_high', 'critical']
        ]
        
        if len(high_risk_zones) >= 3:
            patterns.append({
                'pattern': 'clustered_high_risk',
                'description': f'{len(high_risk_zones)} high-risk zones detected',
                'recommendation': 'Consider site-wide safety review'
            })
        
        # Pattern 2: Disproportionate incidents
        incident_zones = [z for z in heatmap.zones if z['incident_count'] > 2]
        
        if len(incident_zones) > 0:
            total_incidents = sum(z['incident_count'] for z in incident_zones)
            patterns.append({
                'pattern': 'incident_concentration',
                'description': f'{total_incidents} incidents across {len(incident_zones)} zones',
                'affected_zones': [z['zone_id'] for z in incident_zones],
                'recommendation': 'Investigate common factors in incident zones'
            })
        
        # Pattern 3: High occupancy risk
        crowded_zones = [z for z in heatmap.zones if z.get('worker_count', 0) > 15]
        
        if len(crowded_zones) > 0:
            patterns.append({
                'pattern': 'high_occupancy',
                'description': f'{len(crowded_zones)} zones with high worker density',
                'recommendation': 'Consider redistributing workforce'
            })
        
        return patterns
    
    def compare_heatmaps(
        self,
        heatmap1: RiskHeatmap,
        heatmap2: RiskHeatmap
    ) -> Dict[str, Any]:
        """Compare two heatmaps to identify changes"""
        comparison = {
            'period1': heatmap1.time_period,
            'period2': heatmap2.time_period,
            'overall_trend': 'stable',
            'avg_risk_change': 0.0,
            'zones_improved': [],
            'zones_degraded': [],
            'new_hot_spots': []
        }
        
        # Calculate average change
        change = heatmap2.average_risk_score - heatmap1.average_risk_score
        comparison['avg_risk_change'] = round(change, 3)
        
        if change < -0.1:
            comparison['overall_trend'] = 'improving'
        elif change > 0.1:
            comparison['overall_trend'] = 'degrading'
        
        # Compare individual zones
        zones1 = {z['zone_id']: z for z in heatmap1.zones}
        zones2 = {z['zone_id']: z for z in heatmap2.zones}
        
        for zone_id in zones1.keys() & zones2.keys():
            risk_change = zones2[zone_id]['risk_score'] - zones1[zone_id]['risk_score']
            
            if risk_change < -0.2:
                comparison['zones_improved'].append({
                    'zone_id': zone_id,
                    'zone_name': zones2[zone_id]['zone_name'],
                    'improvement': abs(risk_change)
                })
            elif risk_change > 0.2:
                comparison['zones_degraded'].append({
                    'zone_id': zone_id,
                    'zone_name': zones2[zone_id]['zone_name'],
                    'degradation': risk_change
                })
        
        return comparison
    
    def get_stats(self) -> Dict[str, Any]:
        """Get risk mapper statistics"""
        return {
            'total_heatmaps': len(self.heatmaps),
            'zones_tracked': len(self.zone_data)
        }


# Singleton instance
_risk_mapper: Optional[RiskMapper] = None


def get_risk_mapper() -> RiskMapper:
    """Get singleton RiskMapper instance"""
    global _risk_mapper
    
    if _risk_mapper is None:
        _risk_mapper = RiskMapper()
    
    return _risk_mapper
