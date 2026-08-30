from murmur_core.metrics import SessionMetrics


def test_metrics_report_stage_durations():
    metrics = SessionMetrics(started_at=1.0)
    metrics.listening_at = 1.1
    metrics.speech_end_at = 2.0
    metrics.transcript_at = 2.4
    metrics.rewrite_at = 2.6
    metrics.validated_at = 2.7
    metrics.inserted_at = 2.75

    durations = metrics.durations()
    assert round(durations["arming_ms"]) == 100
    assert round(durations["asr_ms"]) == 400
    assert round(durations["rewrite_ms"]) == 200
    assert round(durations["validation_ms"]) == 100
    assert round(durations["insertion_ms"]) == 50
    assert round(durations["total_ms"]) == 1750
