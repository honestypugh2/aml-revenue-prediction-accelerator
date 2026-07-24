"""Redaction and neutrality-scanning helpers."""

from __future__ import annotations

import re

# Patterns for values that must never appear in logs, outputs, or source.
SENSITIVE_PATTERNS: dict[str, re.Pattern[str]] = {
    "azure_subscription_guid": re.compile(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    ),
    "connection_string": re.compile(
        r"(AccountKey|SharedAccessKey|Password)=[^;\s]+", re.IGNORECASE
    ),
    "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*"),
    "sas_token": re.compile(r"[?&]sig=[^&\s]+", re.IGNORECASE),
    "email": re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    "us_phone": re.compile(r"\b\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b"),
}


def contains_potential_secret(text: str) -> bool:
    """Return True if ``text`` matches any sensitive pattern."""
    return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS.values())


def redact(text: str, replacement: str = "[REDACTED]") -> str:
    """Return ``text`` with any matched sensitive values replaced."""
    for pattern in SENSITIVE_PATTERNS.values():
        text = pattern.sub(replacement, text)
    return text


def scan_for_neutrality_violations(text: str) -> list[str]:
    """Return a list of neutrality/secret concerns found in ``text``.

    Used by tests and pre-commit-style checks to guard against accidentally
    embedding secrets or personally identifiable contact information.
    """
    findings: list[str] = []
    for name, pattern in SENSITIVE_PATTERNS.items():
        if pattern.search(text):
            findings.append(name)
    return findings
