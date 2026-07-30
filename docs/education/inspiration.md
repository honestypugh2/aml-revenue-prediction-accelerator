# Educational experience: inspiration and originality

## Conceptual inspiration only

The interactive educational experience in this repository was inspired
**conceptually** by the idea presented in the Microsoft Tech Community article
"ArchAngel: Skilling the next developer generation for the Agentic
transformation": that developers learn best through **contextual,
repository-grounded, interactive guidance** delivered while they work.

## What we took (ideas only)

- The general principle of **learning in context** — lessons and knowledge
  checks tied directly to the code and artifacts in this repository.
- The general principle of making technical education **available through an
  interactive experience** rather than a static document.

## What we did NOT copy

To be unambiguous, **none** of the following were copied from that article or
any associated project:

- source code,
- prose or wording,
- prompts,
- screenshots,
- visual design,
- diagrams,
- branded terminology,
- names, logos, or characters,
- product identity,
- UI structure,
- repository structure (our structure derives from the Azure ML accelerator
  conventions in ADR 0002, independently justified).

## Not a fork or derivative

This project is **not** a fork, reproduction, derivative implementation, or
official implementation of that article or any project it describes. It is an
original educational experience built specifically for **healthcare
net-revenue prediction** with Azure Machine Learning (Automated ML and
code-first), Microsoft Fabric/OneLake, secure Azure infrastructure, MLOps, and
model governance.

## Where the experience lives

- Content: [`src/revenue_prediction/education/`](../../src/revenue_prediction/education/)
  (original lessons, knowledge checks, and the pervasive contextual-note layer).
- Interactive UI: [`frontend/`](../../frontend/) (original React + TypeScript app)
  backed by [`src/revenue_prediction/api/`](../../src/revenue_prediction/api/)
  (FastAPI).
- Workshop materials: [`docs/workshops/`](../workshops/).
