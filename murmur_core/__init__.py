"""Core runtime primitives for Murmur.

The package deliberately keeps platform integrations behind small interfaces so
recording, transcription, rewriting, validation and text injection can evolve
without turning the daemon into a monolith.
"""

from .state import SessionState, SessionStateMachine
from .metrics import SessionMetrics
from .injection import InjectionBroker, YdotoolInjector
from .rewrite import RewriteProvider, OllamaRewriteProvider
from .semantic_lock import SemanticLock, SemanticLockResult

__all__ = [
    "SessionState",
    "SessionStateMachine",
    "SessionMetrics",
    "InjectionBroker",
    "YdotoolInjector",
    "RewriteProvider",
    "OllamaRewriteProvider",
    "SemanticLock",
    "SemanticLockResult",
]
