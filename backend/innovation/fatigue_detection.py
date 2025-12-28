from typing import Dict, List
from datetime import datetime

def detect_fatigue(metrics: List[Dict]) -> Dict:
	"""
	Simple heuristic fatigue detection.

	Args:
		metrics: list of event dicts containing at least a 'duration' or 'eye_closure' key.

	Returns:
		dict with `fatigue` level and score.
	"""
	score = 0
	for m in metrics:
		if not isinstance(m, dict):
			continue
		dur = m.get("duration") or 0
		ec = m.get("eye_closure") or 0
		try:
			score += int(dur) // 60
		except Exception:
			pass
		try:
			score += int(ec)
		except Exception:
			pass

	if score >= 10:
		level = "HIGH"
	elif score >= 4:
		level = "MEDIUM"
	else:
		level = "LOW"

	return {"fatigue": level, "score": score, "checked_at": datetime.utcnow().isoformat()}


__all__ = ["detect_fatigue"]
