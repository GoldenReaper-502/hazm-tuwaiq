from typing import Dict, List
from datetime import datetime

def predict_risk(events: List[Dict]) -> Dict:
    """
    Predict future risk level based on historical unsafe behavior.
    """
    score = len(events)

    if score >= 10:
        level = "CRITICAL"
    elif score >= 5:
        level = "HIGH"
    elif score >= 2:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "predicted_risk": level,
        "score": score,
        "timestamp": datetime.utcnow().isoformat()
    }
