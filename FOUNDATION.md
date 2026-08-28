# MurMur canonical foundation

This branch establishes the non-breaking runtime boundaries for the next MurMur generation.

## Invariants

1. Local/offline operation remains the default.
2. Raw transcript is always available as a safe fallback.
3. LLM cleanup never receives microphone or injection privileges.
4. Global input synthesis is reachable only through an InjectionBroker.
5. Literal high-risk spans (URLs, email addresses, numbers, code/identifier-like text) survive cleanup or the rewrite is rejected.
6. Runtime state has one canonical finite-state machine.
7. Per-session latency is measurable by stage.
8. New providers must implement narrow interfaces rather than modifying the daemon monolith.

## Canonical session lifecycle

`IDLE -> ARMING -> LISTENING -> FINALIZING -> TRANSCRIBING -> REFINING -> VALIDATING -> INSERTING -> COMPLETE -> IDLE`

Terminal states `CANCELLED` and `ERROR` return to `IDLE`.

## Core package

- `murmur_core/state.py` — thread-safe session state machine.
- `murmur_core/metrics.py` — stage latency markers.
- `murmur_core/rewrite.py` — provider-neutral rewrite contract + Ollama provider.
- `murmur_core/semantic_lock.py` — deterministic protected-span validation and raw fallback.
- `murmur_core/pipeline.py` — rewrite -> validate -> deterministic correction composition.
- `murmur_core/injection.py` — privileged input boundary + ydotool implementation.

## Next integration gate

After this foundation passes CI, migrate `daemon.py` incrementally:

1. Replace direct `ydotool` subprocess calls with `YdotoolInjector`.
2. Replace `ollama_cleanup()` with `OllamaRewriteProvider` through `TranscriptPipeline`.
3. Emit state transitions around capture/transcription/rewrite/validation/insertion.
4. Record `SessionMetrics` and log one structured metrics event per dictation.
5. Only then split audio and ASR into their own providers.

This ordering deliberately keeps each change reviewable and preserves the current working Linux behavior.
