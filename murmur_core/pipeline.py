from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .rewrite import PassthroughRewriteProvider, RewriteProvider, RewriteResult
from .semantic_lock import SemanticLock, SemanticLockResult


@dataclass(slots=True, frozen=True)
class PipelineResult:
    raw: str
    rewritten: str
    final: str
    rewrite: RewriteResult
    validation: SemanticLockResult


class TranscriptPipeline:
    """Provider-neutral rewrite + validation + deterministic correction pipeline."""

    def __init__(
        self,
        rewrite_provider: RewriteProvider | None = None,
        semantic_lock: SemanticLock | None = None,
        correction: Callable[[str], str] | None = None,
    ) -> None:
        self.rewrite_provider = rewrite_provider or PassthroughRewriteProvider()
        self.semantic_lock = semantic_lock or SemanticLock()
        self.correction = correction or (lambda text: text)

    def process(self, raw: str, *, vocabulary: Sequence[str] = ()) -> PipelineResult:
        rewrite = self.rewrite_provider.rewrite(raw, vocabulary=vocabulary)
        validation = self.semantic_lock.validate(raw, rewrite.text)
        final = self.correction(validation.output)
        return PipelineResult(raw, rewrite.text, final, rewrite, validation)
