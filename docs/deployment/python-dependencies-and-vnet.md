# Python dependencies and VNet access in Azure ML

Azure Machine Learning does **not** require Conda. Training and inference need a
reproducible runtime image, but that image can be assembled with Conda, `pip`,
`uv`, or a combination of them. Network-isolated workspaces add one constraint:
the environment build and the running compute must have an approved route to
every external package or container source they use.

## Supported dependency patterns

| Pattern | How dependencies are supplied | Best fit |
| --- | --- | --- |
| Curated Azure ML environment | Microsoft maintains the image and common libraries | Exploration and standard frameworks |
| Azure ML environment with Conda YAML | `conda_file` contains Conda packages and an optional `pip:` section | Simple, Azure-native environment builds |
| Azure ML environment with a custom image | A prebuilt image is referenced by digest or immutable tag | Production and network-isolated workloads |
| MLflow no-code deployment | Azure ML uses the environment stored with the logged MLflow model | Standard MLflow models with complete, tested dependency metadata |

Conda YAML is an Azure ML environment input format, not a requirement that every
library come from Conda. This is valid and common:

```yaml
dependencies:
  - python=3.11
  - pip
  - pip:
      - mlflow==2.22.5
      - scikit-learn==1.7.2
```

Plain `pip` is also available in a custom image. `uv` works in Azure ML when it
is used while building that image or from a job command, but Azure ML does not
natively resolve `uv.lock` as an environment definition. For production, build
the locked environment before the job starts:

```dockerfile
COPY pyproject.toml uv.lock ./
RUN python -m pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev
```

Avoid installing dependencies dynamically at the beginning of every training
or scoring run. It increases startup time, weakens reproducibility, and requires
runtime internet or private-feed access.

## Python version choice

This repository supports Python 3.11 and 3.12 (`>=3.11,<3.13`) and exercises
both versions in offline CI. Azure ML training and inference currently use
Python 3.11 because it is the established environment for the registered model,
the selected Azure ML dependencies, and the base image. Staying on 3.11 during
an inference repair also avoids changing the interpreter and model contract at
the same time.

Python 3.12 is the next supported target and can be adopted after the complete
Azure extra, environment image, training job, model serialization, and batch
invocation pass on the target Linux x86_64 platform. A local ARM64 resolver
failure for `azureml-dataprep-native` indicates a missing platform wheel, not a
general Python 3.12 or Azure ML limitation. Python 3.13 and newer are outside
the declared project range and require a deliberate dependency and CI upgrade.

## What changes inside a VNet

Python package management behaves normally inside a VNet; only name resolution,
routing, firewall policy, and authentication change. Treat environment build
traffic separately from job traffic because the image builder and the training
compute can use different network paths.

### Azure ML managed VNet

For a managed-VNet workspace:

1. Create private endpoints for workspace dependencies such as Storage, Key
   Vault, and Azure Container Registry (ACR).
2. Use managed-network outbound rules for approved public package endpoints or
   private endpoints for private services.
3. If packages come from public PyPI, allow HTTPS access to at least
   `pypi.org` and `files.pythonhosted.org`, plus any package-specific download
   hosts. Route traffic through the organization's approved firewall when
   policy requires it.
4. If public outbound access is prohibited, use a private package feed or a
   prebuilt image in ACR.
5. Provision the managed network before a demo or deployment that cannot wait
   for first-use network provisioning.

### Customer-managed VNet

For a BYO VNet, the platform team owns the full path:

- private DNS zones and VNet links;
- NSG rules and user-defined routes;
- Azure Firewall or other egress appliance rules;
- private endpoints for Storage, Key Vault, ACR, and the workspace;
- routes from compute subnets to private package feeds and ACR;
- managed-identity RBAC for image pulls and data access.

Do not assume that successful access from a developer laptop proves access from
Azure ML compute. Validate DNS and HTTPS connectivity from the actual build and
job execution networks.

## Private package feeds

For controlled production environments, mirror approved wheels into Azure
Artifacts or another internal Python Package Index. Configure `pip` or `uv` to
use that index through an authenticated, private route.

- Prefer managed identity or short-lived workload credentials.
- Do not place feed tokens in Dockerfiles, Conda files, source control, or image
  layers.
- Pin versions and retain wheels needed to rebuild historical model versions.
- Mirror transitive dependencies, not only top-level packages.

Package-index configuration can be supplied through approved CI secrets or
runtime environment configuration. Secret material must not be logged or stored
in the registered Azure ML environment definition.

## Recommended production pattern

For this accelerator:

1. Resolve and test dependencies with `uv` in CI.
2. Build a versioned inference image from the lock file in a controlled build
   network.
3. Push the image to private ACR and reference it from an Azure ML environment
   by immutable digest where practical.
4. Package the fitted estimator **with** its leakage-safe feature builder and
   explicit scoring contract.
5. Run a batch endpoint invocation against synthetic checkpoint data before
   promotion.

MLflow no-code deployment remains useful when the logged model includes the
complete preprocessing pipeline and a tested, pinned environment. Do not rely
on automatically inferred dependencies without building and invoking the model
in a representative environment first.

## Validation checklist

- Environment image builds without unrestricted internet access.
- Azure ML compute can pull the image from ACR using managed identity.
- Compute can read input and write output through private endpoints and RBAC.
- Package installation does not occur during ordinary scoring startup.
- The model artifact contains preprocessing and estimator state together.
- A synthetic batch invocation completes and produces the expected schema.

See also:

- [Security and networking](../security/networking.md)
- [Deployment guide](guide.md)
- [Inference in production](../operations/inference-in-production.md)
- [Azure ML managed network guidance](https://learn.microsoft.com/azure/machine-learning/how-to-managed-network)
- [Secure workspace tutorial](https://learn.microsoft.com/azure/machine-learning/tutorial-create-secure-workspace)