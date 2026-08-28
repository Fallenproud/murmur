from __future__ import annotations

from dataclasses import dataclass
import re


_PROTECTED_PATTERNS = (
    re.compile(r"https?://\S+", re.I),
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b\d+(?:[.,:]\d+)*\b"),
    re.compile(r"`[^`]+`"),
    re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:[-_.][A-Za-z0-9_]+)+\b"),
)


@dataclass(slots=True, frozen=True)
class SemanticLockResult:
    accepted: bool
    output: str
    reason: str
    protected_before: tuple[str, ...]
    protected_after: tuple[str, ...]


class SemanticLock:
    """Deterministic first safety layer for LLM cleanup.

    This is intentionally conservative. It does not claim to solve semantic
    equivalence; it prevents a class of high-cost rewrite errors by ensuring
    obvious literal spans survive cleanup. A future embedding/NLI validator can
    sit behind the same API.
    """

    @staticmethod
    def protected_spans(text: str) -> tuple[str, ...]:
        spans: list[tuple[int, str]] = []
        for pattern in _PROTECTED_PATTERNS:
            spans.extend((m.start(), m.group(0)) for m in pattern.finditer(text))
        spans.sort(key=lambda item: item[0])
        return tuple(value for _, value in spans)

    def validate(self, raw: str, candidate: str) -> SemanticLockResult:
        before = self.protected_spans(raw)
        after = self.protected_spans(candidate)
        missing = [span for span in before if span not in after]
        if missing:
            return SemanticLockResult(
                accepted=False,
                output=raw,
                reason="protected spans changed or disappeared: " + ", ".join(missing),
                protected_before=before,
                protected_after=after,
            )
        if raw.strip() and not candidate.strip():
            return SemanticLockResult(False, raw, "rewrite produced empty output", before, after)
        return SemanticLockResult(True, candidate, "accepted", before, after)
