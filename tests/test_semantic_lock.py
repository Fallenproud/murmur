from murmur_core.semantic_lock import SemanticLock


def test_accepts_safe_cleanup():
    lock = SemanticLock()
    result = lock.validate(
        "um deploy version 1.42 to api-prod",
        "Deploy version 1.42 to api-prod.",
    )
    assert result.accepted
    assert result.output == "Deploy version 1.42 to api-prod."


def test_rejects_changed_identifier():
    lock = SemanticLock()
    result = lock.validate(
        "deploy version 1.42 to api-prod",
        "Deploy version 1.43 to api-production.",
    )
    assert not result.accepted
    assert result.output == "deploy version 1.42 to api-prod"


def test_rejects_removed_url():
    lock = SemanticLock()
    raw = "send this to https://example.com/a?q=1"
    result = lock.validate(raw, "Send this to the website.")
    assert not result.accepted
    assert result.output == raw
