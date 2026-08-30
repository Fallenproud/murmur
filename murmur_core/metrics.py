from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass(slots=True)
class SessionMetrics:
    """Per-dictation latency markers.

    Values are monotonic timestamps. `durations()` returns seconds between the
    important user-visible stages and is intentionally provider-agnostic.
    """

    started_at: float = field(default_factory=time.monotonic)
    listening_at: float | None = None
    speech_end_at: float | None = None
    transcript_at: float | None = None
    rewrite_at: float | None = None
    validated_at: float | None = None
    inserted_at: float | None = None

    def mark(self, name: str) -> None:
        if not hasattr(self, name):
            raise AttributeError(name)
        setattr(self, name, time.monotonic())

    def durations(self) -> dict[str, float]:
        out: dict[str, float] = {}
        if self.listening_at is not None:
            out["arming_ms"] = (self.listening_at - self.started_at) * 1000
        if self.speech_end_at is not None and self.transcript_at is not None:
            out["asr_ms"] = (self.transcript_at - self.speech_end_at) * 1000
        if self.transcript_at is not None and self.rewrite_at is not None:
            out["rewrite_ms"] = (self.rewrite_at - self.transcript_at) * 1000
        if self.rewrite_at is not None and self.validated_at is not None:
            out["validation_ms"] = (self.validated_at - self.rewrite_at) * 1000
        if self.validated_at is not None and self.inserted_at is not None:
            out["insertion_ms"] = (self.inserted_at - self.validated_at) * 1000
        if self.inserted_at is not None:
            out["total_ms"] = (self.inserted_at - self.started_at) * 1000
        return out
