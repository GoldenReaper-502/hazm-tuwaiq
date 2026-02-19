"""CCTV service abstraction with safe fallback to stub implementation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    objects: list[dict[str, Any]]
    provider: str


class CCTVImplementation:
    def detect(
        self, frame_bytes: bytes
    ) -> DetectionResult:  # pragma: no cover - interface
        raise NotImplementedError


class RealCCTVImplementation(CCTVImplementation):
    def __init__(self):
        try:
            from backend import ai_engine

            self.ai_engine = ai_engine
            self.provider = "backend.ai_engine"
        except Exception as e:
            raise RuntimeError(f"Real CCTV engine unavailable: {e}")

    def detect(self, frame_bytes: bytes) -> DetectionResult:
        result = self.ai_engine.detect_frame(frame_bytes)
        objects = result.get("objects", []) if isinstance(result, dict) else []
        return DetectionResult(objects=objects, provider=self.provider)


class StubCCTVImplementation(CCTVImplementation):
    def detect(self, frame_bytes: bytes) -> DetectionResult:
        _ = frame_bytes
        return DetectionResult(objects=[], provider="stub")


class CCTVService:
    def __init__(self):
        try:
            self.impl: CCTVImplementation = RealCCTVImplementation()
        except Exception as e:
            logger.warning("Falling back to stub CCTV implementation: %s", e)
            self.impl = StubCCTVImplementation()

    def detect_image(self, frame_bytes: bytes) -> DetectionResult:
        return self.impl.detect(frame_bytes)


cctv_service = CCTVService()
