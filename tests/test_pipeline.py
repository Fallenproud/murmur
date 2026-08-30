from murmur_core.pipeline import TranscriptPipeline
from murmur_core.rewrite import RewriteResult


class Rewriter:
    def __init__(self, output: str):
        self.output = output

    def rewrite(self, text: str, *, vocabulary=()):
        return RewriteResult(self.output, "test", self.output != text)


def test_pipeline_accepts_safe_rewrite_then_applies_correction():
    pipeline = TranscriptPipeline(
        rewrite_provider=Rewriter("Deploy version 1.42 to api-prod."),
        correction=lambda text: text.replace("api-prod", "API-PROD"),
    )
    result = pipeline.process("um deploy version 1.42 to api-prod")
    assert result.validation.accepted
    assert result.final == "Deploy version 1.42 to API-PROD."


def test_pipeline_falls_back_when_protected_span_changes():
    raw = "deploy version 1.42 to api-prod"
    pipeline = TranscriptPipeline(rewrite_provider=Rewriter("Deploy version 1.43 to api-production."))
    result = pipeline.process(raw)
    assert not result.validation.accepted
    assert result.final == raw
