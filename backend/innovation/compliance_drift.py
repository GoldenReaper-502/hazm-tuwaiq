from typing import Dict, List
from datetime import datetime

def detect_compliance_drift(records: List[Dict]) -> Dict:
	"""Simple heuristic to detect compliance drift.

	Counts number of rule-violation-like entries and returns a drift level.
	"""
	score = 0
	for r in records:
		if not isinstance(r, dict):
			continue
		if r.get("violation"):
			score += 2
		if r.get("confidence") and r.get("confidence") < 0.6:
			score += 1

	if score >= 8:
		level = "HIGH"
	elif score >= 3:
		level = "MEDIUM"
	else:
		level = "LOW"

	return {"drift_level": level, "score": score, "checked_at": datetime.utcnow().isoformat()}


__all__ = ["detect_compliance_drift"]
