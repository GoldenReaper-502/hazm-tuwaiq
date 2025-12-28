from typing import Dict, List
from datetime import datetime

def analyze_root_cause(events: List[Dict]) -> Dict:
	"""Return a simple aggregated root-cause analysis summary.

	This is intentionally lightweight and deterministic for import/validation.
	"""
	counts = {}
	for e in events:
		if not isinstance(e, dict):
			continue
		reason = e.get("reason") or "unknown"
		counts[reason] = counts.get(reason, 0) + 1

	primary = max(counts.items(), key=lambda x: x[1])[0] if counts else None
	return {"primary_cause": primary, "counts": counts, "analyzed_at": datetime.utcnow().isoformat()}


__all__ = ["analyze_root_cause"]
