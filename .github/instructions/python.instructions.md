---
applyTo: "src/**/*.py"
---

# Python source instructions

- Target Python 3.11+; use type hints and Pydantic v2 models for config.
- Keep optional cloud/UI imports **guarded** (import inside functions or under
  `try/except ImportError`) so the core package imports without extras.
- Preserve leakage safety: never let a feature use post-snapshot information;
  fit preprocessing on training data only.
- Prefer numpy arrays for numeric math to keep Pyright noise-free (pandas
  dynamic typing widens unions).
- Add tests under `tests/` for new behavior. Run `make check` before finishing.
- No `print` in library code paths that are not CLI/entry points; use return
  values or `rich` in the CLI.
