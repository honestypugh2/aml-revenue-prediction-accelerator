# Pull request

## Summary

<!-- What does this change and why? -->

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Documentation
- [ ] Infrastructure / MLOps
- [ ] Refactor / chore

## Checklist

- [ ] Customer-neutral: no customer/patient/organization data, no secrets or
      resource identifiers (used placeholders like `FAC-001`,
      `WORKSPACE_PLACEHOLDER`).
- [ ] Synthetic data only.
- [ ] Leakage safety preserved (no future info in features; time-aware splits).
- [ ] `uv run ruff check src tests` passes.
- [ ] `uv run ruff format --check src tests` passes.
- [ ] `uv run pyright src` passes.
- [ ] `uv run pytest` passes.
- [ ] Docs / `THIRD_PARTY_NOTICES.md` / ADRs updated where relevant.
- [ ] Cloud-touching code keeps imports guarded and live tests opt-in.
