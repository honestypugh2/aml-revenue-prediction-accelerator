"""Lessons and knowledge checks (original content)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Lesson:
    """A single self-guided lesson."""

    key: str
    title: str
    summary: str
    body: str
    references: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class KnowledgeCheck:
    """A multiple-choice knowledge check with a single correct answer."""

    key: str
    question: str
    options: list[str]
    correct_index: int
    explanation: str


@dataclass(frozen=True)
class ContextualNote:
    """A short, in-context learning note pinned to a specific area of the app.

    Contextual notes power the *pervasive* self-guided experience: wherever the
    learner is (dataset overview, training, predictions, governance, ...), a
    relevant, bite-sized note explains what they are looking at and why it
    matters, and links to a deeper lesson.
    """

    area: str
    title: str
    detail: str
    lesson_key: str | None = None
    tip: str | None = None


_LESSONS: list[Lesson] = [
    Lesson(
        key="problem_framing",
        title="Framing the problem: partial-month net-revenue prediction",
        summary="Why this is decision support, at facility-month-snapshot grain.",
        body=(
            "The accelerator estimates month-end **net revenue** for a facility "
            "using only information available *as of* a snapshot date (for "
            "example, day 15). The prediction grain is facility x accounting "
            "month x snapshot date. The actual target is only known after "
            "accounting close, so inference can run repeatedly during the month "
            "without retraining. This is operational decision support and "
            "financial forecasting - not clinical decision support, financial "
            "advice, or an autonomous decision system."
        ),
        references=["docs/architecture/adr/0001-modeling-grain.md", "docs/modeling/strategy.md"],
    ),
    Lesson(
        key="billing_vs_net_revenue",
        title="Billing amount is not net revenue",
        summary="Gross charges must be reduced by contractuals, denials, and bad debt.",
        body=(
            "Gross charges (billed amounts) overstate what an organization will "
            "actually collect. **Net revenue** subtracts contractual "
            "adjustments, denials, bad debt, and charity care. The synthetic "
            "generator models these effects explicitly so learners can see why "
            "a naive 'sum of charges' is a poor proxy for the target."
        ),
        references=["data/README.md", "docs/modeling/strategy.md"],
    ),
    Lesson(
        key="leakage_safety",
        title="Leakage safety and time-aware validation",
        summary="Never use future information; split by month, not by random row.",
        body=(
            "A feature for a snapshot must never use information from after that "
            "snapshot date. We forbid post-close columns as inputs, fit "
            "preprocessing only on training data, and split by *accounting "
            "month* so all snapshots of a facility-month stay together. Random "
            "row splitting would leak future months into the past and inflate "
            "metrics - so it is not used as the primary evaluation method."
        ),
        references=["docs/modeling/strategy.md", "docs/architecture/adr/0004-leakage-safety.md"],
    ),
    Lesson(
        key="automl_vs_code_first",
        title="Two Azure ML v2 approaches: AutoML and code-first",
        summary="When to reach for Automated ML vs a code-first pipeline.",
        body=(
            "Automated ML (SDK v2) quickly searches models and preprocessing for "
            "a strong baseline with built-in explainability. Code-first training "
            "gives full control of features, validation, and model choice, and "
            "is easier to govern and reproduce. The accelerator ships both and "
            "compares them fairly using the same time-aware test block."
        ),
        references=["notebooks/automl", "notebooks/code_first", "docs/modeling/strategy.md"],
    ),
    Lesson(
        key="fabric_onelake",
        title="Microsoft Fabric and OneLake integration",
        summary="Read inputs and write Power BI-ready predictions to a Lakehouse.",
        body=(
            "OneLake exposes an ADLS Gen2 endpoint. The accelerator reads "
            "snapshot inputs from a Lakehouse and writes a flat, typed "
            "predictions table back to OneLake so a Power BI DirectLake semantic "
            "model can consume it without copies. A local fallback keeps the "
            "demo fully offline."
        ),
        references=["docs/fabric/integration.md", "fabric/README.md"],
    ),
    Lesson(
        key="governance",
        title="Governance: champion/challenger, registration, responsible AI",
        summary="Compare models, register the champion, document responsible AI.",
        body=(
            "The champion is the best model on the held-out test block; the "
            "challenger is the runner-up (or a new candidate during retraining). "
            "Only a challenger that beats the incumbent by a configured margin is "
            "promotable. Registration, explainability, and a responsible AI "
            "review precede any production use."
        ),
        references=["docs/governance/responsible-ai.md", "docs/governance/model-governance.md"],
    ),
    Lesson(
        key="security_infra",
        title="Secure Azure infrastructure",
        summary="Managed VNet, private endpoints, and least-privilege identity.",
        body=(
            "Production workspaces should use network isolation (managed VNet or "
            "BYO VNet), private endpoints, private DNS, and managed identity with "
            "least-privilege RBAC. No secrets are committed; all identifiers are "
            "placeholders supplied via environment variables at deploy time."
        ),
        references=["docs/security/networking.md", "infra/README.md"],
    ),
]


_CHECKS: list[KnowledgeCheck] = [
    KnowledgeCheck(
        key="grain",
        question="What is the prediction grain of the default demonstration?",
        options=[
            "Patient x encounter x diagnosis",
            "Facility x accounting month x snapshot date",
            "Facility x calendar day",
            "Payer x service line x year",
        ],
        correct_index=1,
        explanation=(
            "The reusable demonstration uses facility-month-snapshot grain; "
            "patient/encounter inputs are a documented future extension."
        ),
    ),
    KnowledgeCheck(
        key="split",
        question="Why is random row splitting avoided for evaluation?",
        options=[
            "It is slower than temporal splitting",
            "It leaks future months into training and inflates metrics",
            "scikit-learn does not support it",
            "It requires a GPU",
        ],
        correct_index=1,
        explanation=(
            "Random splitting mixes future and past, leaking information and "
            "producing optimistic, unreliable metrics."
        ),
    ),
    KnowledgeCheck(
        key="target",
        question="Which best describes the target, actual_month_end_net_revenue?",
        options=[
            "Sum of gross charges to date",
            "Known in real time at every snapshot",
            "Only known after accounting close",
            "A patient-level billing amount",
        ],
        correct_index=2,
        explanation="Net revenue is finalized after close, which is why we predict it early.",
    ),
    KnowledgeCheck(
        key="onelake",
        question="How does the accelerator access OneLake?",
        options=[
            "A proprietary Fabric-only protocol",
            "The ADLS Gen2 endpoint with DefaultAzureCredential",
            "By copying data to a local SQL Server",
            "Through anonymous public URLs",
        ],
        correct_index=1,
        explanation=(
            "OneLake is ADLS Gen2-compatible; the client uses "
            "azure-storage-file-datalake with DefaultAzureCredential."
        ),
    ),
    KnowledgeCheck(
        key="promotion",
        question="When is a challenger model promotable over the champion?",
        options=[
            "Whenever it has any lower error at all",
            "Only when it beats the incumbent by the configured margin",
            "Never - the champion is fixed",
            "When it uses a deep neural network",
        ],
        correct_index=1,
        explanation=(
            "A configured improvement threshold prevents promoting models on "
            "noise; governance review still applies."
        ),
    ),
]


def get_lessons() -> list[Lesson]:
    """Return all lessons in presentation order."""
    return list(_LESSONS)


def get_knowledge_checks() -> list[KnowledgeCheck]:
    """Return all knowledge-check questions."""
    return list(_CHECKS)


def grade_answer(check: KnowledgeCheck, chosen_index: int) -> bool:
    """Return True if ``chosen_index`` is the correct answer for ``check``."""
    return chosen_index == check.correct_index


# ---------------------------------------------------------------------------
# Contextual notes: the pervasive, in-context learning layer.
# Keyed by "area" so any surface (React UI, notebook, workshop) can pull the
# relevant notes for wherever the learner currently is.
# ---------------------------------------------------------------------------
AREAS: tuple[str, ...] = (
    "overview",
    "data",
    "training",
    "evaluation",
    "predictions",
    "governance",
    "fabric",
    "security",
)

_CONTEXTUAL_NOTES: list[ContextualNote] = [
    ContextualNote(
        area="overview",
        title="You are looking at synthetic revenue-cycle data",
        detail=(
            "Each row is one facility-month-snapshot. The chart shows a "
            "facility's actual month-end net revenue over time - the value we "
            "learn to predict early, from within-month signal."
        ),
        lesson_key="problem_framing",
        tip="Pick different facilities to see how seasonality and scale differ.",
    ),
    ContextualNote(
        area="data",
        title="Billing is not net revenue",
        detail=(
            "month_to_date_gross_charges is a billed amount. The target is net "
            "of contractual adjustments, denials, bad debt, and charity care - "
            "which is why a naive sum of charges over-predicts."
        ),
        lesson_key="billing_vs_net_revenue",
        tip="Compare gross charges to the target for the same facility-month.",
    ),
    ContextualNote(
        area="data",
        title="Historical features use only closed months",
        detail=(
            "prior_month, prior_year, and rolling windows are derived strictly "
            "from months before the current one - never from the future."
        ),
        lesson_key="leakage_safety",
    ),
    ContextualNote(
        area="training",
        title="Why baselines run first",
        detail=(
            "naive_prior and seasonal_naive set the bar. A complex model must "
            "beat them to earn its place; sometimes, on little data, it does "
            "not - and that is a real, useful result."
        ),
        lesson_key="automl_vs_code_first",
        tip="Watch the comparison table: does the champion beat both baselines?",
    ),
    ContextualNote(
        area="training",
        title="Time-aware splits, never random rows",
        detail=(
            "The most recent months are the test block; earlier months train. "
            "All snapshots of a facility-month stay together to prevent leakage."
        ),
        lesson_key="leakage_safety",
    ),
    ContextualNote(
        area="evaluation",
        title="Read accuracy by snapshot day",
        detail=(
            "Error should generally shrink as the month progresses and more "
            "signal accrues. Accuracy by facility reveals where the model is "
            "systematically weaker."
        ),
        lesson_key="problem_framing",
        tip="If day-27 error is not better than day-7, investigate the features.",
    ),
    ContextualNote(
        area="predictions",
        title="Every prediction is self-describing",
        detail=(
            "Outputs carry model name/version, run id, cutoff day, and scoring "
            "timestamp, plus uncertainty where available - so any number is "
            "traceable to the exact model that produced it."
        ),
        lesson_key="governance",
    ),
    ContextualNote(
        area="governance",
        title="Champion vs challenger",
        detail=(
            "The champion is best on the held-out test block; the challenger is "
            "the runner-up. A challenger is promotable only if it beats the "
            "incumbent by the configured margin - guarding against noise."
        ),
        lesson_key="governance",
    ),
    ContextualNote(
        area="fabric",
        title="Power BI-ready output via OneLake",
        detail=(
            "Predictions are written as a flat, typed table a Fabric DirectLake "
            "semantic model can read without copies. A local fallback keeps the "
            "demo fully offline."
        ),
        lesson_key="fabric_onelake",
    ),
    ContextualNote(
        area="security",
        title="No secrets, ever",
        detail=(
            "All identifiers are placeholders supplied via environment "
            "variables. Auth uses DefaultAzureCredential; production adds "
            "network isolation and private endpoints."
        ),
        lesson_key="security_infra",
    ),
]


def get_contextual_notes(area: str | None = None) -> list[ContextualNote]:
    """Return contextual notes, optionally filtered to a single ``area``."""
    if area is None:
        return list(_CONTEXTUAL_NOTES)
    return [note for note in _CONTEXTUAL_NOTES if note.area == area]


def get_lesson(key: str) -> Lesson | None:
    """Return a single lesson by key, or ``None`` if not found."""
    for lesson in _LESSONS:
        if lesson.key == key:
            return lesson
    return None
