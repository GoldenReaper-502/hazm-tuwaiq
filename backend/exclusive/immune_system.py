"""
HAZM TUWAIQ - Safety Immune System
Self-learning, adaptive safety system that evolves and strengthens over time
Like a biological immune system, it learns from past incidents and builds resistance
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from enum import Enum


class ThreatLevel(str, Enum):
    """Threat severity levels"""
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class ImmuneResponse(str, Enum):
    """Types of immune responses"""
    PASSIVE_MONITORING = "passive_monitoring"
    ACTIVE_SURVEILLANCE = "active_surveillance"
    CONTAINMENT = "containment"
    ELIMINATION = "elimination"
    QUARANTINE = "quarantine"


class SafetyAntibody:
    """
    Safety antibody - learned response to specific threat patterns
    Like biological antibodies, these are created after exposure to threats
    """
    
    def __init__(
        self,
        antibody_id: str,
        threat_signature: Dict[str, Any],
        effectiveness: float,
        created_from_incident: str
    ):
        self.antibody_id = antibody_id
        self.threat_signature = threat_signature  # Pattern that triggers this antibody
        self.effectiveness = effectiveness  # 0-1, how well it neutralizes threats
        self.created_from_incident = created_from_incident
        self.activation_count = 0
        self.last_activation = None
        self.success_rate = 0.0
        self.created_at = datetime.now()
        
    def activate(self, threat: Dict[str, Any]) -> bool:
        """Activate antibody against a threat"""
        self.activation_count += 1
        self.last_activation = datetime.now()
        
        # Check if threat matches signature
        match_score = self._calculate_match(threat)
        
        return match_score >= 0.7  # 70% match threshold
    
    def _calculate_match(self, threat: Dict[str, Any]) -> float:
        """Calculate how well threat matches this antibody's signature"""
        matches = 0
        total = len(self.threat_signature)
        
        for key, value in self.threat_signature.items():
            if key in threat and threat[key] == value:
                matches += 1
        
        return matches / total if total > 0 else 0.0
    
    def update_effectiveness(self, success: bool):
        """Update effectiveness based on outcome"""
        # Moving average
        alpha = 0.3  # Learning rate
        outcome = 1.0 if success else 0.0
        self.effectiveness = alpha * outcome + (1 - alpha) * self.effectiveness
        self.success_rate = self.effectiveness


class SafetyImmuneSystem:
    """
    Biological-inspired immune system for workplace safety
    
    Features:
    - Memory: Remembers past incidents and builds antibodies
    - Adaptation: Learns new threat patterns
    - Recognition: Identifies similar threats quickly
    - Response: Escalates response based on threat severity
    - Evolution: Strengthens over time with more exposure
    """
    
    def __init__(self):
        self.antibodies: Dict[str, SafetyAntibody] = {}
        self.threat_memory: List[Dict[str, Any]] = []
        self.immune_strength = 0.5  # 0-1, overall system strength
        self.active_threats: Dict[str, Dict[str, Any]] = {}
        self.neutralized_threats = 0
        self.total_exposures = 0
        
        # Immune system parameters
        self.memory_retention_days = 365  # How long to keep threat memory
        self.antibody_generation_threshold = 2  # Incidents before creating antibody
        self.adaptation_rate = 0.1  # How quickly system adapts
        
    def expose(self, incident: Dict[str, Any]) -> ImmuneResponse:
        """
        Expose system to an incident (like exposing immune system to pathogen)
        System learns and adapts from this exposure
        """
        self.total_exposures += 1
        
        # Extract threat signature
        threat_signature = self._extract_threat_signature(incident)
        threat_level = self._assess_threat_level(incident)
        
        # Store in memory
        self.threat_memory.append({
            'incident': incident,
            'signature': threat_signature,
            'level': threat_level,
            'timestamp': datetime.now()
        })
        
        # Check if we have antibodies for this threat
        matching_antibody = self._find_matching_antibody(threat_signature)
        
        if matching_antibody:
            # Known threat - activate antibody
            if matching_antibody.activate(threat_signature):
                return self._antibody_response(matching_antibody, incident)
        else:
            # New threat - check if we should create antibody
            similar_count = self._count_similar_incidents(threat_signature)
            
            if similar_count >= self.antibody_generation_threshold:
                # Create new antibody
                antibody = self._create_antibody(threat_signature, incident)
                self.antibodies[antibody.antibody_id] = antibody
                print(f"🧬 New safety antibody created: {antibody.antibody_id}")
        
        # Determine response based on threat level
        return self._determine_response(threat_level, matching_antibody is not None)
    
    def _extract_threat_signature(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Extract identifying pattern from incident"""
        signature = {
            'type': incident.get('type'),
            'location': incident.get('location'),
            'severity': incident.get('severity'),
            'conditions': incident.get('environmental_conditions', {}),
            'time_pattern': self._extract_time_pattern(incident.get('timestamp'))
        }
        return signature
    
    def _extract_time_pattern(self, timestamp: Optional[datetime]) -> str:
        """Extract time-based pattern (hour, day of week, etc.)"""
        if not timestamp:
            return 'unknown'
        
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        hour = timestamp.hour
        
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def _assess_threat_level(self, incident: Dict[str, Any]) -> ThreatLevel:
        """Assess severity of threat"""
        severity = incident.get('severity', 'low')
        
        if severity == 'fatal' or incident.get('fatalities', 0) > 0:
            return ThreatLevel.CRITICAL
        elif severity == 'critical' or incident.get('injuries', 0) > 2:
            return ThreatLevel.SEVERE
        elif severity == 'high' or incident.get('injuries', 0) > 0:
            return ThreatLevel.MODERATE
        elif severity == 'medium' or incident.get('near_miss', False):
            return ThreatLevel.SUSPICIOUS
        else:
            return ThreatLevel.BENIGN
    
    def _find_matching_antibody(self, threat_signature: Dict[str, Any]) -> Optional[SafetyAntibody]:
        """Find antibody that matches threat signature"""
        best_match = None
        best_score = 0.0
        
        for antibody in self.antibodies.values():
            score = self._calculate_signature_similarity(
                antibody.threat_signature,
                threat_signature
            )
            
            if score > best_score and score >= 0.7:
                best_score = score
                best_match = antibody
        
        return best_match
    
    def _calculate_signature_similarity(
        self,
        sig1: Dict[str, Any],
        sig2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two threat signatures"""
        matches = 0
        total = len(sig1)
        
        for key, value in sig1.items():
            if key in sig2 and sig2[key] == value:
                matches += 1
        
        return matches / total if total > 0 else 0.0
    
    def _count_similar_incidents(self, threat_signature: Dict[str, Any]) -> int:
        """Count how many similar incidents exist in memory"""
        count = 0
        
        for memory in self.threat_memory:
            similarity = self._calculate_signature_similarity(
                memory['signature'],
                threat_signature
            )
            
            if similarity >= 0.7:
                count += 1
        
        return count
    
    def _create_antibody(
        self,
        threat_signature: Dict[str, Any],
        incident: Dict[str, Any]
    ) -> SafetyAntibody:
        """Create new antibody from incident exposure"""
        antibody_id = f"AB-{len(self.antibodies) + 1:04d}"
        
        antibody = SafetyAntibody(
            antibody_id=antibody_id,
            threat_signature=threat_signature,
            effectiveness=0.5,  # Start at 50% effectiveness
            created_from_incident=incident.get('id', 'unknown')
        )
        
        return antibody
    
    def _antibody_response(
        self,
        antibody: SafetyAntibody,
        incident: Dict[str, Any]
    ) -> ImmuneResponse:
        """Execute antibody-mediated response"""
        
        # Antibody is highly effective - quick elimination
        if antibody.effectiveness >= 0.8:
            self.neutralized_threats += 1
            antibody.update_effectiveness(True)
            return ImmuneResponse.ELIMINATION
        
        # Moderate effectiveness - containment
        elif antibody.effectiveness >= 0.5:
            antibody.update_effectiveness(True)
            return ImmuneResponse.CONTAINMENT
        
        # Low effectiveness - active surveillance
        else:
            return ImmuneResponse.ACTIVE_SURVEILLANCE
    
    def _determine_response(
        self,
        threat_level: ThreatLevel,
        has_antibody: bool
    ) -> ImmuneResponse:
        """Determine appropriate immune response"""
        
        if threat_level == ThreatLevel.CRITICAL:
            return ImmuneResponse.ELIMINATION
        
        elif threat_level == ThreatLevel.SEVERE:
            return ImmuneResponse.CONTAINMENT if has_antibody else ImmuneResponse.QUARANTINE
        
        elif threat_level == ThreatLevel.MODERATE:
            return ImmuneResponse.CONTAINMENT if has_antibody else ImmuneResponse.ACTIVE_SURVEILLANCE
        
        elif threat_level == ThreatLevel.SUSPICIOUS:
            return ImmuneResponse.ACTIVE_SURVEILLANCE
        
        else:
            return ImmuneResponse.PASSIVE_MONITORING
    
    def strengthen(self, training_data: List[Dict[str, Any]]):
        """Strengthen immune system through training (vaccination-like)"""
        print("💉 Vaccinating safety immune system...")
        
        for incident in training_data:
            self.expose(incident)
        
        # Update overall immune strength
        if self.total_exposures > 0:
            neutralization_rate = self.neutralized_threats / self.total_exposures
            self.immune_strength = min(1.0, 0.5 + neutralization_rate * 0.5)
        
        print(f"✅ Immune strength: {self.immune_strength:.2%}")
        print(f"🧬 Active antibodies: {len(self.antibodies)}")
    
    def scan_environment(self, current_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactive scanning for potential threats
        Like white blood cells patrolling the body
        """
        detected_risks = []
        
        # Check current conditions against known threat signatures
        for antibody in self.antibodies.values():
            similarity = self._calculate_signature_similarity(
                antibody.threat_signature,
                current_conditions
            )
            
            if similarity >= 0.5:  # Potential match
                detected_risks.append({
                    'antibody_id': antibody.antibody_id,
                    'threat_type': antibody.threat_signature.get('type'),
                    'match_confidence': similarity,
                    'recommended_action': 'preventive_measures',
                    'effectiveness': antibody.effectiveness
                })
        
        return detected_risks
    
    def get_immune_status(self) -> Dict[str, Any]:
        """Get comprehensive immune system status"""
        
        # Clean old memories
        self._cleanup_old_memories()
        
        # Calculate statistics
        active_antibodies = len(self.antibodies)
        highly_effective = sum(1 for ab in self.antibodies.values() if ab.effectiveness >= 0.8)
        
        avg_effectiveness = np.mean([ab.effectiveness for ab in self.antibodies.values()]) if self.antibodies else 0.0
        
        return {
            'immune_strength': self.immune_strength,
            'total_antibodies': active_antibodies,
            'highly_effective_antibodies': highly_effective,
            'average_antibody_effectiveness': avg_effectiveness,
            'total_exposures': self.total_exposures,
            'neutralized_threats': self.neutralized_threats,
            'neutralization_rate': self.neutralized_threats / self.total_exposures if self.total_exposures > 0 else 0.0,
            'memory_size': len(self.threat_memory),
            'system_age_days': (datetime.now() - self.antibodies[list(self.antibodies.keys())[0]].created_at).days if self.antibodies else 0
        }
    
    def _cleanup_old_memories(self):
        """Remove old threat memories to maintain system efficiency"""
        cutoff_date = datetime.now() - timedelta(days=self.memory_retention_days)
        
        self.threat_memory = [
            memory for memory in self.threat_memory
            if memory['timestamp'] > cutoff_date
        ]
    
    def export_antibodies(self) -> List[Dict[str, Any]]:
        """Export antibodies for sharing or backup"""
        return [
            {
                'id': ab.antibody_id,
                'signature': ab.threat_signature,
                'effectiveness': ab.effectiveness,
                'activations': ab.activation_count,
                'success_rate': ab.success_rate,
                'created_at': ab.created_at.isoformat()
            }
            for ab in self.antibodies.values()
        ]
    
    def import_antibodies(self, antibody_data: List[Dict[str, Any]]):
        """Import antibodies from another system (transfer immunity)"""
        print("🔄 Importing antibodies (transfer immunity)...")
        
        for data in antibody_data:
            antibody = SafetyAntibody(
                antibody_id=data['id'],
                threat_signature=data['signature'],
                effectiveness=data['effectiveness'],
                created_from_incident='imported'
            )
            antibody.activation_count = data.get('activations', 0)
            antibody.success_rate = data.get('success_rate', 0.0)
            
            self.antibodies[antibody.antibody_id] = antibody
        
        print(f"✅ Imported {len(antibody_data)} antibodies")


# Global immune system instance
safety_immune_system = SafetyImmuneSystem()
