from __future__ import annotations

from dataclasses import dataclass
import json
import urllib.request
from typing import Protocol, Sequence


@dataclass(slots=True, frozen=True)
class RewriteResult:
    text: str
    provider: str
    changed: bool
    fallback: bool = False


class RewriteProvider(Protocol):
    def rewrite(self, text: str, *, vocabulary: Sequence[str] = ()) -> RewriteResult: ...


class PassthroughRewriteProvider:
    def rewrite(self, text: str, *, vocabulary: Sequence[str] = ()) -> RewriteResult:
        return RewriteResult(text=text, provider="passthrough", changed=False)


class OllamaRewriteProvider:
    """Conservative local rewrite provider.

    The provider deliberately cannot perform text injection or access microphone
    state. It receives text and returns text, which keeps the trust boundary
    narrow and makes it directly testable.
    """

    def __init__(self, *, base_url: str, model: str, timeout: float = 12.0, keepalive: str = "10m") -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.keepalive = keepalive

    @staticmethod
    def _prompt(text: str, vocabulary: Sequence[str]) -> str:
        vocab_line = ", ".join(vocabulary) if vocabulary else "(none)"
        return (
            "You clean up raw speech-to-text dictation. Apply ONLY these edits:\n"
            "- remove only clear verbal disfluencies: um, uh, er, mm, hmm\n"
            "- fix punctuation, capitalization, and obvious mis-transcriptions\n"
            "- preserve every other word, meaning, number, identifier, URL, email, command, and quoted phrase\n"
            "- known proper nouns may only be corrected when already an obvious phonetic match: " + vocab_line + "\n"
            "- leave garbled or low-confidence passages unchanged instead of inventing text\n"
            "Do NOT rephrase, summarize, translate, answer, or add commentary.\n"
            "Output ONLY the cleaned text.\n\n"
            "Text: " + text + "\nCleaned:"
        )

    def rewrite(self, text: str, *, vocabulary: Sequence[str] = ()) -> RewriteResult:
        body = json.dumps({
            "model": self.model,
            "prompt": self._prompt(text, vocabulary),
            "stream": False,
            "keep_alive": self.keepalive,
            "options": {"temperature": 0},
        }).encode()
        request = urllib.request.Request(
            self.base_url + "/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                cleaned = json.loads(response.read())["response"].strip()
            # Models occasionally add a label despite instructions. Strip only a
            # narrow leading label; do not heuristically truncate user content.
            for prefix in ("Cleaned:", "Output:", "Text:"):
                if cleaned.lower().startswith(prefix.lower()):
                    cleaned = cleaned[len(prefix):].lstrip()
                    break
            cleaned = cleaned.strip().strip('"').strip()
            if not cleaned:
                cleaned = text
            return RewriteResult(cleaned, f"ollama:{self.model}", cleaned != text)
        except Exception:
            return RewriteResult(text, f"ollama:{self.model}", False, fallback=True)
