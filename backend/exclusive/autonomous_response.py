"""
HAZM TUWAIQ - Enhanced Autonomous Response System
AI-driven autonomous safety response with decision-making capabilities
Self-healing safety system that acts without human intervention
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class ResponseLevel(str, Enum):
    """Autonomy levels for responses"""
    MONITOR = "monitor"  # Just observe
    NOTIFY = "notify"  # Alert humans
    ASSIST = "assist"  # Suggest actions
    EXECUTE = "execute"  # Execute with confirmation
    AUTONOMOUS = "autonomous"  # Full autonomy


class ActionType(str, Enum):
    """Types of autonomous actions"""
    ALERT_WORKER = "alert_worker"
    STOP_EQUIPMENT = "stop_equipment"
    ACTIVATE_SAFETY_SYSTEM = "activate_safety_system"
    EVACUATE_AREA = "evacuate_area"
    CALL_EMERGENCY = "call_emergency"
    LOCKOUT_ZONE = "lockout_zone"
    ADJUST_ENVIRONMENT = "adjust_environment"
    REROUTE_TRAFFIC = "reroute_traffic"
    ACTIVATE_VENTILATION = "activate_ventilation"
    DEPLOY_BARRIER = "deploy_barrier"


class ActionStatus(str, Enum):
    """Status of autonomous action"""
    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PENDING_APPROVAL = "pending_approval"


@dataclass
class Incident:
    """Safety incident requiring response"""
    incident_id: str
    timestamp: datetime
    incident_type: str
    severity: str  # low, medium, high, critical
    location: str
    description: str
    affected_workers: List[str]
    risk_score: float  # 0-100
    confidence: float  # 0-1
    

@dataclass
class AutonomousAction:
    """Autonomous action to be taken"""
    action_id: str
    incident_id: str
    action_type: ActionType
    response_level: ResponseLevel
    target: str  # Equipment, zone, worker, etc.
    parameters: Dict[str, Any]
    priority: int  # 1-10, 10 being highest
    estimated_execution_time: float  # seconds
    safety_impact: str  # Expected safety improvement
    status: ActionStatus
    created_at: datetime
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    

@dataclass
class DecisionLog:
    """Log of autonomous decision"""
    decision_id: str
    timestamp: datetime
    incident_id: str
    decision_rationale: str
    considered_actions: List[str]
    selected_action: str
    confidence: float
    override_available: bool
    human_approval_required: bool
    

class EnhancedAutonomousResponse:
    """
    Enhanced autonomous response system with AI decision-making
    
    Features:
    - Multi-level autonomy (from monitoring to full autonomous action)
    - Intelligent action selection based on context
    - Self-learning from outcomes
    - Safety-first decision making
    - Human override capabilities
    - Audit trail for all actions
    """
    
    def __init__(self):
        self.active_incidents: Dict[str, Incident] = {}
        self.action_queue: List[AutonomousAction] = []
        self.action_history: List[AutonomousAction] = []
        self.decision_log: List[DecisionLog] = []
        
        # Learning: action effectiveness tracking
        self.action_effectiveness: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {'success_rate': 0.5, 'avg_response_time': 0.0, 'execution_count': 0}
        )
        
        # Autonomy levels by incident severity
        self.autonomy_policy = {
            'critical': ResponseLevel.AUTONOMOUS,  # Full autonomy for critical incidents
            'high': ResponseLevel.EXECUTE,  # Execute with minimal delay
            'medium': ResponseLevel.ASSIST,  # Suggest actions
            'low': ResponseLevel.NOTIFY  # Just notify
        }
        
        # Action response times (seconds)
        self.response_times = {
            ActionType.ALERT_WORKER: 1.0,
            ActionType.STOP_EQUIPMENT: 2.0,
            ActionType.ACTIVATE_SAFETY_SYSTEM: 3.0,
            ActionType.EVACUATE_AREA: 5.0,
            ActionType.CALL_EMERGENCY: 10.0,
            ActionType.LOCKOUT_ZONE: 4.0,
            ActionType.ADJUST_ENVIRONMENT: 15.0,
            ActionType.REROUTE_TRAFFIC: 8.0,
            ActionType.ACTIVATE_VENTILATION: 12.0,
            ActionType.DEPLOY_BARRIER: 6.0
        }
    
    def process_incident(self, incident: Incident) -> List[AutonomousAction]:
        """
        Process an incident and determine autonomous response
        
        Returns list of actions to be taken
        """
        
        # Store incident
        self.active_incidents[incident.incident_id] = incident
        
        # Determine appropriate autonomy level
        response_level = self._determine_response_level(incident)
        
        # Generate possible actions
        possible_actions = self._generate_action_options(incident)
        
        # Select best action(s) using AI decision-making
        selected_actions = self._select_optimal_actions(
            incident,
            possible_actions,
            response_level
        )
        
        # Log decision
        self._log_decision(incident, possible_actions, selected_actions)
        
        # Queue actions for execution
        for action in selected_actions:
            self.action_queue.append(action)
        
        # Execute autonomous actions immediately
        autonomous_actions = [
            a for a in selected_actions
            if a.response_level == ResponseLevel.AUTONOMOUS
        ]
        
        for action in autonomous_actions:
            self._execute_action(action)
        
        return selected_actions
    
    def _determine_response_level(self, incident: Incident) -> ResponseLevel:
        """Determine appropriate autonomy level for incident"""
        
        # Check policy
        policy_level = self.autonomy_policy.get(incident.severity, ResponseLevel.NOTIFY)
        
        # Adjust based on confidence
        if incident.confidence < 0.7:
            # Low confidence - reduce autonomy
            levels = [ResponseLevel.MONITOR, ResponseLevel.NOTIFY, ResponseLevel.ASSIST,
                     ResponseLevel.EXECUTE, ResponseLevel.AUTONOMOUS]
            current_index = levels.index(policy_level)
            adjusted_index = max(0, current_index - 1)
            return levels[adjusted_index]
        
        return policy_level
    
    def _generate_action_options(self, incident: Incident) -> List[AutonomousAction]:
        """Generate possible actions for an incident"""
        
        actions = []
        action_counter = len(self.action_history) + 1
        
        # Severity-based action generation
        if incident.severity in ['critical', 'high']:
            # Critical/High: Immediate protective actions
            
            # Stop equipment
            if 'equipment' in incident.incident_type.lower():
                actions.append(AutonomousAction(
                    action_id=f"ACT-{action_counter:06d}",
                    incident_id=incident.incident_id,
                    action_type=ActionType.STOP_EQUIPMENT,
                    response_level=ResponseLevel.AUTONOMOUS,
                    target=incident.location,
                    parameters={'immediate': True},
                    priority=10,
                    estimated_execution_time=self.response_times[ActionType.STOP_EQUIPMENT],
                    safety_impact="Prevent equipment-related injury",
                    status=ActionStatus.PLANNED,
                    created_at=datetime.now()
                ))
                action_counter += 1
            
            # Alert workers in area
            actions.append(AutonomousAction(
                action_id=f"ACT-{action_counter:06d}",
                incident_id=incident.incident_id,
                action_type=ActionType.ALERT_WORKER,
                response_level=ResponseLevel.AUTONOMOUS,
                target=incident.location,
                parameters={
                    'workers': incident.affected_workers,
                    'alert_type': 'visual_audio'
                },
                priority=9,
                estimated_execution_time=self.response_times[ActionType.ALERT_WORKER],
                safety_impact="Warn workers of immediate danger",
                status=ActionStatus.PLANNED,
                created_at=datetime.now()
            ))
            action_counter += 1
            
            # Evacuate if critical
            if incident.severity == 'critical':
                actions.append(AutonomousAction(
                    action_id=f"ACT-{action_counter:06d}",
                    incident_id=incident.incident_id,
                    action_type=ActionType.EVACUATE_AREA,
                    response_level=ResponseLevel.AUTONOMOUS,
                    target=incident.location,
                    parameters={'evacuation_radius': 50},  # meters
                    priority=10,
                    estimated_execution_time=self.response_times[ActionType.EVACUATE_AREA],
                    safety_impact="Remove personnel from danger zone",
                    status=ActionStatus.PLANNED,
                    created_at=datetime.now()
                ))
                action_counter += 1
            
            # Activate safety systems
            if 'fire' in incident.incident_type.lower():
                actions.append(AutonomousAction(
                    action_id=f"ACT-{action_counter:06d}",
                    incident_id=incident.incident_id,
                    action_type=ActionType.ACTIVATE_SAFETY_SYSTEM,
                    response_level=ResponseLevel.AUTONOMOUS,
                    target="fire_suppression",
                    parameters={'zone': incident.location},
                    priority=10,
                    estimated_execution_time=self.response_times[ActionType.ACTIVATE_SAFETY_SYSTEM],
                    safety_impact="Suppress fire before spread",
                    status=ActionStatus.PLANNED,
                    created_at=datetime.now()
                ))
                action_counter += 1
            
            # Gas leak - ventilation
            if 'gas' in incident.incident_type.lower():
                actions.append(AutonomousAction(
                    action_id=f"ACT-{action_counter:06d}",
                    incident_id=incident.incident_id,
                    action_type=ActionType.ACTIVATE_VENTILATION,
                    response_level=ResponseLevel.AUTONOMOUS,
                    target=incident.location,
                    parameters={'fan_speed': 'max'},
                    priority=9,
                    estimated_execution_time=self.response_times[ActionType.ACTIVATE_VENTILATION],
                    safety_impact="Dilute hazardous atmosphere",
                    status=ActionStatus.PLANNED,
                    created_at=datetime.now()
                ))
                action_counter += 1
            
            # Call emergency services
            if incident.severity == 'critical':
                actions.append(AutonomousAction(
                    action_id=f"ACT-{action_counter:06d}",
                    incident_id=incident.incident_id,
                    action_type=ActionType.CALL_EMERGENCY,
                    response_level=ResponseLevel.EXECUTE,  # Requires confirmation
                    target="emergency_services",
                    parameters={
                        'service_type': 'fire_ambulance',
                        'incident_details': incident.description
                    },
                    priority=8,
                    estimated_execution_time=self.response_times[ActionType.CALL_EMERGENCY],
                    safety_impact="Ensure professional emergency response",
                    status=ActionStatus.PLANNED,
                    created_at=datetime.now()
                ))
                action_counter += 1
        
        elif incident.severity == 'medium':
            # Medium: Preventive actions
            
            # Alert worker
            actions.append(AutonomousAction(
                action_id=f"ACT-{action_counter:06d}",
                incident_id=incident.incident_id,
                action_type=ActionType.ALERT_WORKER,
                response_level=ResponseLevel.ASSIST,
                target=incident.location,
                parameters={'workers': incident.affected_workers},
                priority=5,
                estimated_execution_time=self.response_times[ActionType.ALERT_WORKER],
                safety_impact="Warn workers of potential hazard",
                status=ActionStatus.PLANNED,
                created_at=datetime.now()
            ))
            action_counter += 1
            
            # Lockout zone
            if incident.risk_score > 60:
                actions.append(AutonomousAction(
                    action_id=f"ACT-{action_counter:06d}",
                    incident_id=incident.incident_id,
                    action_type=ActionType.LOCKOUT_ZONE,
                    response_level=ResponseLevel.ASSIST,
                    target=incident.location,
                    parameters={'access_level': 'restricted'},
                    priority=6,
                    estimated_execution_time=self.response_times[ActionType.LOCKOUT_ZONE],
                    safety_impact="Prevent access to hazardous area",
                    status=ActionStatus.PLANNED,
                    created_at=datetime.now()
                ))
        
        else:
            # Low: Monitoring and notification
            actions.append(AutonomousAction(
                action_id=f"ACT-{action_counter:06d}",
                incident_id=incident.incident_id,
                action_type=ActionType.ALERT_WORKER,
                response_level=ResponseLevel.NOTIFY,
                target="safety_supervisor",
                parameters={'notification_type': 'low_priority'},
                priority=2,
                estimated_execution_time=self.response_times[ActionType.ALERT_WORKER],
                safety_impact="Keep supervisor informed",
                status=ActionStatus.PLANNED,
                created_at=datetime.now()
            ))
        
        return actions
    
    def _select_optimal_actions(
        self,
        incident: Incident,
        possible_actions: List[AutonomousAction],
        response_level: ResponseLevel
    ) -> List[AutonomousAction]:
        """Select optimal actions using AI decision-making"""
        
        if not possible_actions:
            return []
        
        # Filter by response level
        filtered_actions = [
            a for a in possible_actions
            if self._is_action_allowed(a, response_level)
        ]
        
        if not filtered_actions:
            return []
        
        # Score each action
        scored_actions = []
        for action in filtered_actions:
            score = self._score_action(action, incident)
            scored_actions.append((action, score))
        
        # Sort by score
        scored_actions.sort(key=lambda x: x[1], reverse=True)
        
        # Select top actions (avoid redundancy)
        selected = []
        selected_types = set()
        
        for action, score in scored_actions:
            # Avoid duplicate action types unless high priority
            if action.action_type not in selected_types or action.priority >= 9:
                selected.append(action)
                selected_types.add(action.action_type)
            
            # Limit to 5 simultaneous actions
            if len(selected) >= 5:
                break
        
        return selected
    
    def _is_action_allowed(self, action: AutonomousAction, max_level: ResponseLevel) -> bool:
        """Check if action is allowed at given autonomy level"""
        
        levels = [ResponseLevel.MONITOR, ResponseLevel.NOTIFY, ResponseLevel.ASSIST,
                 ResponseLevel.EXECUTE, ResponseLevel.AUTONOMOUS]
        
        action_index = levels.index(action.response_level)
        max_index = levels.index(max_level)
        
        return action_index <= max_index
    
    def _score_action(self, action: AutonomousAction, incident: Incident) -> float:
        """Score an action's suitability (0-100)"""
        
        score = 0.0
        
        # Priority contributes heavily
        score += action.priority * 10.0
        
        # Historical effectiveness
        action_key = action.action_type.value
        if action_key in self.action_effectiveness:
            effectiveness = self.action_effectiveness[action_key]
            score += effectiveness['success_rate'] * 20.0
        
        # Speed bonus (faster actions score higher for high severity)
        if incident.severity in ['critical', 'high']:
            time_factor = 1.0 / (1.0 + action.estimated_execution_time / 10.0)
            score += time_factor * 15.0
        
        # Confidence penalty
        if incident.confidence < 0.8:
            score *= incident.confidence
        
        return score
    
    def _execute_action(self, action: AutonomousAction):
        """Execute an autonomous action"""
        
        action.status = ActionStatus.EXECUTING
        action.executed_at = datetime.now()
        
        # Simulate action execution
        # In real system, this would interface with physical/digital controls
        
        try:
            # Action-specific execution logic
            if action.action_type == ActionType.STOP_EQUIPMENT:
                result = self._stop_equipment(action.target)
            elif action.action_type == ActionType.ALERT_WORKER:
                result = self._alert_worker(action.parameters.get('workers', []))
            elif action.action_type == ActionType.EVACUATE_AREA:
                result = self._evacuate_area(action.target, action.parameters)
            elif action.action_type == ActionType.ACTIVATE_SAFETY_SYSTEM:
                result = self._activate_safety_system(action.target, action.parameters)
            elif action.action_type == ActionType.CALL_EMERGENCY:
                result = self._call_emergency(action.parameters)
            else:
                result = f"Executed {action.action_type.value}"
            
            action.status = ActionStatus.COMPLETED
            action.result = result
            action.completed_at = datetime.now()
            
            # Update effectiveness
            self._update_effectiveness(action, success=True)
            
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.result = f"Failed: {str(e)}"
            action.completed_at = datetime.now()
            
            # Update effectiveness
            self._update_effectiveness(action, success=False)
        
        # Move to history
        self.action_history.append(action)
        if action in self.action_queue:
            self.action_queue.remove(action)
    
    def _stop_equipment(self, target: str) -> str:
        """Stop equipment (simulated)"""
        return f"Equipment stopped at {target}"
    
    def _alert_worker(self, workers: List[str]) -> str:
        """Alert workers (simulated)"""
        return f"Alert sent to {len(workers)} worker(s)"
    
    def _evacuate_area(self, location: str, parameters: Dict) -> str:
        """Evacuate area (simulated)"""
        radius = parameters.get('evacuation_radius', 30)
        return f"Evacuation initiated for {location} (radius: {radius}m)"
    
    def _activate_safety_system(self, system: str, parameters: Dict) -> str:
        """Activate safety system (simulated)"""
        return f"Safety system '{system}' activated with params: {parameters}"
    
    def _call_emergency(self, parameters: Dict) -> str:
        """Call emergency services (simulated)"""
        service = parameters.get('service_type', 'general')
        return f"Emergency call placed to {service}"
    
    def _update_effectiveness(self, action: AutonomousAction, success: bool):
        """Update action effectiveness based on outcome"""
        
        action_key = action.action_type.value
        stats = self.action_effectiveness[action_key]
        
        # Update success rate (moving average)
        alpha = 0.2
        current_rate = stats['success_rate']
        new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
        stats['success_rate'] = new_rate
        
        # Update execution count
        stats['execution_count'] += 1
        
        # Update average response time
        if action.executed_at and action.created_at:
            response_time = (action.executed_at - action.created_at).total_seconds()
            stats['avg_response_time'] = (
                alpha * response_time +
                (1 - alpha) * stats['avg_response_time']
            )
    
    def _log_decision(
        self,
        incident: Incident,
        possible_actions: List[AutonomousAction],
        selected_actions: List[AutonomousAction]
    ):
        """Log autonomous decision for audit trail"""
        
        decision = DecisionLog(
            decision_id=f"DEC-{len(self.decision_log) + 1:06d}",
            timestamp=datetime.now(),
            incident_id=incident.incident_id,
            decision_rationale=self._generate_rationale(incident, selected_actions),
            considered_actions=[a.action_type.value for a in possible_actions],
            selected_action=", ".join([a.action_type.value for a in selected_actions]),
            confidence=incident.confidence,
            override_available=True,
            human_approval_required=any(
                a.response_level == ResponseLevel.EXECUTE for a in selected_actions
            )
        )
        
        self.decision_log.append(decision)
    
    def _generate_rationale(
        self,
        incident: Incident,
        selected_actions: List[AutonomousAction]
    ) -> str:
        """Generate human-readable decision rationale"""
        
        rationale = f"Incident severity: {incident.severity}, Risk score: {incident.risk_score:.0f}. "
        
        if selected_actions:
            actions_str = ", ".join([a.action_type.value for a in selected_actions])
            rationale += f"Selected actions: {actions_str}. "
            rationale += f"Priority: {max([a.priority for a in selected_actions])}."
        else:
            rationale += "No autonomous action required - monitoring only."
        
        return rationale
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get autonomous response system status"""
        
        return {
            'active_incidents': len(self.active_incidents),
            'queued_actions': len(self.action_queue),
            'completed_actions_today': len([
                a for a in self.action_history
                if a.completed_at and (datetime.now() - a.completed_at).days == 0
            ]),
            'success_rate': np.mean([
                stats['success_rate']
                for stats in self.action_effectiveness.values()
            ]) if self.action_effectiveness else 0.0,
            'average_response_time': np.mean([
                stats['avg_response_time']
                for stats in self.action_effectiveness.values()
                if stats['avg_response_time'] > 0
            ]) if self.action_effectiveness else 0.0,
            'autonomy_levels': dict(self.autonomy_policy),
            'action_effectiveness': dict(self.action_effectiveness)
        }


# Global enhanced autonomous response instance
enhanced_autonomous_response = EnhancedAutonomousResponse()
