"""Smart report generation from detection results.

Generates summaries, risk scores, and recommended actions based on detected objects.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime


# Hazard classification and risk scoring
HAZARD_MAPPING = {
    "person": {"risk": 0.5, "category": "Personnel"},
    "car": {"risk": 0.4, "category": "Vehicle"},
    "truck": {"risk": 0.6, "category": "Vehicle"},
    "motorcycle": {"risk": 0.7, "category": "Vehicle"},
    "bicycle": {"risk": 0.3, "category": "Vehicle"},
    "dog": {"risk": 0.4, "category": "Animal"},
    "cat": {"risk": 0.2, "category": "Animal"},
    "other": {"risk": 0.3, "category": "Unknown"},
}


def calculate_risk_score(objects: List[Dict[str, Any]]) -> float:
    """Calculate overall risk score (0.0-1.0) from detected objects."""
    if not objects:
        return 0.0
    scores = []
    for obj in objects:
        cls = obj.get("class", "other").lower()
        confidence = obj.get("confidence", 0.5)
        hazard_info = HAZARD_MAPPING.get(cls, HAZARD_MAPPING["other"])
        risk = hazard_info["risk"] * confidence
        scores.append(risk)
    return min(1.0, sum(scores) / max(1, len(scores)))


def generate_summary(objects: List[Dict[str, Any]]) -> str:
    """Generate text summary of detected objects."""
    if not objects:
        return "No objects detected."
    parts = [f"Detected {len(objects)} object(s):"]
    for obj in objects[:5]:  # top 5
        cls = obj.get("class", "unknown")
        conf = obj.get("confidence", 0.0)
        parts.append(f"  - {cls} ({conf*100:.1f}%)")
    return "\n".join(parts)


def generate_recommendations(risk_score: float, objects: List[Dict[str, Any]]) -> List[str]:
    """Generate action recommendations based on risk level and detections."""
    rec = []
    if risk_score > 0.7:
        rec.append("⚠️ HIGH RISK: Immediate inspection and safety review recommended")
    elif risk_score > 0.4:
        rec.append("⚡ MEDIUM RISK: Standard monitoring and logging")
    else:
        rec.append("✓ LOW RISK: Continue routine operations")
    
    for obj in objects:
        cls = obj.get("class", "").lower()
        if "person" in cls:
            rec.append("Ensure proper ID verification and access control")
        if "vehicle" in cls or any(x in cls for x in ["car", "truck", "motorcycle"]):
            rec.append("Verify vehicle authorization and safety compliance")
    
    return rec


def generate_report(
    detection_id: str,
    objects: List[Dict[str, Any]],
    location: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a complete smart report from detection data."""
    if not timestamp:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    risk_score = calculate_risk_score(objects)
    summary = generate_summary(objects)
    recommendations = generate_recommendations(risk_score, objects)
    
    return {
        "id": f"rpt_{detection_id[4:]}",  # rpt_000001
        "detection_id": detection_id,
        "timestamp": timestamp,
        "location": location or "Unknown",
        "risk_score": round(risk_score, 2),
        "risk_level": "HIGH" if risk_score > 0.7 else ("MEDIUM" if risk_score > 0.4 else "LOW"),
        "objects_count": len(objects),
        "summary": summary,
        "recommendations": recommendations,
        "objects": objects,
    }
