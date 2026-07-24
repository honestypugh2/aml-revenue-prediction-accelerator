---
applyTo: "infra/**"
---

# Infrastructure instructions

- Default to **private/secure** configurations in the secure profiles: disable
  public network access, firewall dependencies, use private endpoints and
  private DNS.
- Never hard-code subscription/tenant IDs, secrets, or resource names. Derive
  names from a prefix + a random suffix; take identifiers as variables/params.
- Keep three profiles coherent: quickstart (public), secure (managed VNet +
  private endpoints + Bastion/jump box), and BYO-VNet foundation.
- Validate Bicep with `az bicep build`. Validate Terraform with
  `terraform fmt -check`, `terraform init -backend=false`, `terraform validate`.
- Prefer least-privilege RBAC. Document required roles in
  `docs/security/networking.md`.
- Any reuse of the reference infrastructure must remain attributed in
  `THIRD_PARTY_NOTICES.md` (MIT).
