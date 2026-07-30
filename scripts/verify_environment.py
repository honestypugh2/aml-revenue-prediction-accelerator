#!/usr/bin/env python
"""Environment verification and customer-neutrality / secret scanning.

Usage:
    python scripts/verify_environment.py                 # verify local env
    python scripts/verify_environment.py --neutrality-scan  # scan repo for secrets/PII

The neutrality scan is used by pre-commit. It scans tracked text files for
patterns that must never be committed (GUIDs, connection strings, tokens, SAS
signatures, emails, phone numbers) and fails if any are found outside allowed
example/placeholder contexts.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files/globs allowed to contain pattern-like text (examples/tests/docs of the
# patterns themselves). Kept deliberately small.
ALLOWLIST_SUFFIXES = {".lock"}
ALLOWLIST_PATHS = {
    "scripts/verify_environment.py",
    "src/revenue_prediction/security/redaction.py",
    "tests/unit/test_metrics_monitoring_security.py",
    "SECURITY.md",
    ".env.example",
}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".tf",
    ".bicep",
    ".bicepparam",
    ".cfg",
    ".ini",
    ".txt",
    ".sh",
    ".ps1",
}


def _tracked_files() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        files = [REPO_ROOT / line for line in out.stdout.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        skip_dirs = {".venv", ".git", "__pycache__", "outputs", "mlruns", ".ruff_cache", ".pytest_cache"}
        files = [
            p
            for p in REPO_ROOT.rglob("*")
            if p.is_file() and not any(part in skip_dirs for part in p.parts)
        ]
    return [f for f in files if f.suffix in TEXT_SUFFIXES]


def neutrality_scan() -> int:
    from revenue_prediction.security.redaction import scan_for_neutrality_violations

    violations: list[str] = []
    for path in _tracked_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in ALLOWLIST_PATHS or path.suffix in ALLOWLIST_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        # Ignore obvious placeholders.
        findings = scan_for_neutrality_violations(text)
        # Emails inside example/docs contact guidance are the only likely FP; we
        # do not allowlist them broadly — real contact info should not be here.
        if findings:
            violations.append(f"{rel}: {sorted(set(findings))}")

    if violations:
        print("Neutrality/secret scan FAILED. Potential issues:")
        for v in violations:
            print("  -", v)
        print("\nRemove secrets/PII and use neutral placeholders (FAC-001, WORKSPACE_PLACEHOLDER).")
        return 1
    print("Neutrality/secret scan passed: no secrets or contact PII detected.")
    return 0


def verify_env() -> int:
    ok = True
    print(f"Python: {sys.version.split()[0]}")

    def _check(name: str, mod: str) -> None:
        nonlocal ok
        try:
            __import__(mod)
            print(f"  [ok] {name}")
        except ImportError:
            print(f"  [--] {name} (not installed)")
            if mod in {"pandas", "sklearn", "pydantic"}:
                ok = False

    print("Core dependencies:")
    for name, mod in [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("xgboost", "xgboost"),
        ("pandera", "pandera"),
        ("mlflow", "mlflow"),
        ("pydantic", "pydantic"),
    ]:
        _check(name, mod)

    print("Optional integrations:")
    for name, mod in [
        ("azure-ai-ml", "azure.ai.ml"),
        ("azure-identity", "azure.identity"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("azure-storage-file-datalake", "azure.storage.filedatalake"),
    ]:
        _check(name, mod)

    try:
        from revenue_prediction.config.loader import load_settings

        settings = load_settings("dev")
        print("Configuration:")
        print(f"  environment = {settings.environment}")
        print(f"  azure_ml configured = {settings.azure_ml.is_configured()}")
        print(f"  fabric configured   = {settings.fabric.is_configured()}")
    except Exception as exc:  # pragma: no cover
        print(f"  [--] could not load settings: {exc}")
        ok = False

    print("\nOK" if ok else "\nEnvironment has issues (see above).")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--neutrality-scan", action="store_true", help="Scan repo for secrets/PII"
    )
    args = parser.parse_args()
    return neutrality_scan() if args.neutrality_scan else verify_env()


if __name__ == "__main__":
    raise SystemExit(main())
