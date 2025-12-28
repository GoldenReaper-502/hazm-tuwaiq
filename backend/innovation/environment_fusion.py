from typing import Dict, List, Any
from datetime import datetime

def fuse_environment(sensors: List[Dict[str, Any]]) -> Dict:
	"""Merge simple sensor readings into a single environment snapshot.

	This is a lightweight, deterministic fusion used for tests and import checks.
	"""
	snapshot = {"sources": len(sensors), "values": {}, "created_at": datetime.utcnow().isoformat()}
	for s in sensors:
		if not isinstance(s, dict):
			continue
		for k, v in s.items():
			if k == "id":
				continue
			# prefer latest value
			snapshot["values"][k] = v

	return snapshot


__all__ = ["fuse_environment"]
