# Cost control & cleanup

> Cloud resources cost money even when idle. Follow this guide to avoid
> surprises. All commands are examples; substitute your own resource names.

## Biggest cost drivers

| Resource | Cost note | Mitigation |
| --- | --- | --- |
| Compute cluster | Charged while nodes are up | Set `min_instances=0`; enable idle scale-down |
| Managed online endpoint | Charged while provisioned | Delete when not in use; batch-first |
| Azure Bastion | Hourly charge | Deploy only in secure profile; delete when idle |
| Jump box VM | Charged while running | Deallocate when not needed |
| Storage / OneLake | Per-GB | Lifecycle policies; clean scratch data |

## Prefer batch inference

Batch scoring (no always-on endpoint) is the default and cheapest path. Only
provision a managed online endpoint when low-latency, on-demand scoring is
required, and delete it afterward.

## Scale compute to zero

Create clusters with `min_instances=0` so they scale down when idle. Verify no
long-running jobs are pinning nodes.

## Delete when done

```bash
# Delete an online endpoint (and its deployments)
az ml online-endpoint delete --name <endpoint> -g <rg> -w <workspace> --yes

# Delete a compute cluster
az ml compute delete --name cpu-cluster -g <rg> -w <workspace> --yes
```

## Tear down infrastructure

```bash
# Terraform profiles
cd infra/terraform-quickstart && terraform destroy
cd infra/terraform          && terraform destroy   # secure profile (Bastion, VM, PEs)

# Bicep: delete the resource group (irreversible)
az group delete --name <rg> --yes
```

Deleting a resource group is **destructive and irreversible**. Confirm you are
targeting the correct group and that no other workloads share it.

## Offline-first for learning

The entire education/workshop path runs offline with `uv sync --extra ui` and the
synthetic generator — zero cloud cost. Use the cloud only when demonstrating the
Azure ML / Fabric integration.
