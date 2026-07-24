"""Security helpers: neutrality checks and log redaction.

These utilities help keep the accelerator customer-neutral and prevent
accidental logging of secrets. They intentionally use conservative,
well-tested patterns rather than exhaustive DLP.
"""

from __future__ import annotations

from .redaction import (
    SENSITIVE_PATTERNS,
    contains_potential_secret,
    redact,
    scan_for_neutrality_violations,
)

__all__ = [
    "SENSITIVE_PATTERNS",
    "contains_potential_secret",
    "redact",
    "scan_for_neutrality_violations",
]
