"""Lessons and knowledge checks (original content)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace


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
    KnowledgeCheck(
        key="leakage_gate",
        question=(
            "At the leakage gate, why is month_end_close_flag dropped before "
            "scoring a mid-month snapshot?"
        ),
        options=[
            "It is always constant, so it adds no value",
            "It is only known after accounting close, so using it would leak "
            "the future into an as-of prediction",
            "It is a patient identifier that must be redacted",
            "The model cannot accept boolean columns",
        ],
        correct_index=1,
        explanation=(
            "month_end_close_flag is a post-close field. A feature for a "
            "snapshot must never use information from after its snapshot_date, "
            "so the contract drops it (and other post-close fields) at scoring."
        ),
    ),
    KnowledgeCheck(
        key="lineage",
        question=(
            "Each prediction row carries model_name, model_version, and run_id. "
            "Why does that matter for finance?"
        ),
        options=[
            "It makes the output file smaller",
            "It is required by scikit-learn",
            "Lineage - every number is traceable to the exact model that " "produced it",
            "It replaces the need for monitoring",
        ],
        correct_index=2,
        explanation=(
            "Self-describing predictions attach model identity and run id, so "
            "any figure in a Power BI report is auditable back to the model "
            "version and run that generated it."
        ),
    ),
    KnowledgeCheck(
        key="inference_target",
        question=("Inference validates the snapshot with require_target=False. Why?"),
        options=[
            "To make scoring run faster",
            "Because the target is optional metadata",
            "Because the month-end target is not known mid-month, so scoring "
            "must not require it",
            "Because the target is always zero before close",
        ],
        correct_index=2,
        explanation=(
            "actual_month_end_net_revenue is only known after close. At each "
            "intra-month checkpoint we score without it, using the same data "
            "contract in inference mode (require_target=False)."
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


# --- Delivery-planning content: success criteria & data readiness ----------


@dataclass(frozen=True)
class MetricTarget:
    """A working accuracy target for one mid-month checkpoint."""

    checkpoint: str
    primary_metric: str
    target: str
    must_beat: str


@dataclass(frozen=True)
class SuccessCriterion:
    """A business KPI or adoption gate that defines "done" for the POC."""

    category: str  # "Business KPI" or "Adoption gate"
    name: str
    target: str


@dataclass(frozen=True)
class ReadinessDimension:
    """A data-readiness dimension rated red / amber / green."""

    key: str
    dimension: str
    description: str
    default_rating: str  # "green" | "amber" | "red"
    is_gate: bool
    guidance: str


SUCCESS_HEADLINE = (
    "Facility-level net revenue within +/-3-5% at day 15 (WAPE <= 4%), beating "
    "the manual analyst estimate, and trusted enough that finance acts on it."
)

_METRIC_TARGETS: list[MetricTarget] = [
    MetricTarget("Day 10 (early read)", "WAPE", "<= 5-7% (directional)", "Manual analyst estimate"),
    MetricTarget(
        "Day 15 (primary)",
        "WAPE + bias",
        "<= 4% at system; +/-3-5% by facility",
        "Manual analyst estimate",
    ),
    MetricTarget("Day 21 (second)", "WAPE", "<= 4%", "Manual analyst estimate"),
    MetricTarget(
        "Pre-close (final)",
        "WAPE + interval coverage",
        "<= 4%; ~80% interval coverage",
        "Manual analyst estimate",
    ),
]

_SUCCESS_CRITERIA: list[SuccessCriterion] = [
    SuccessCriterion(
        "Business KPI",
        "Forecast accuracy vs. manual mid-month estimate",
        "Beat the manual analyst baseline",
    ),
    SuccessCriterion(
        "Business KPI", "Days-earlier-to-insight", "A reliable read by day 15, before close"
    ),
    SuccessCriterion(
        "Business KPI",
        "Reduction in month-end surprise",
        "Shrink the mid-month vs. final gap, by facility",
    ),
    SuccessCriterion("Business KPI", "Analyst effort saved", "Fewer hours hand-building estimates"),
    SuccessCriterion(
        "Adoption gate",
        "Workflow integration",
        "Prediction auto-populates the existing Power BI report",
    ),
    SuccessCriterion(
        "Adoption gate", "Refresh reliability", "Predictions land on time at each checkpoint"
    ),
    SuccessCriterion(
        "Adoption gate",
        "Explainability",
        "Key drivers are visible so finance can challenge them",
    ),
    SuccessCriterion(
        "Adoption gate", "Governance sign-off", "Aggregate-only, no PHI; access confirmed"
    ),
    SuccessCriterion(
        "Adoption gate", "Trust threshold", "Model beats the manual estimate before anyone acts"
    ),
]

_READINESS: list[ReadinessDimension] = [
    ReadinessDimension(
        "datasets",
        "Available datasets",
        "Source tables identified and reachable in Fabric/OneLake.",
        "green",
        False,
        "Prefer a single source of truth over ungoverned extracts.",
    ),
    ReadinessDimension(
        "grain",
        "Data grain",
        "Transaction/encounter rows roll up cleanly to facility-month.",
        "green",
        False,
        "Confirm keys join without a grain mismatch.",
    ),
    ReadinessDimension(
        "history",
        "Historical depth",
        ">= 24 months of comparable facility-level history for training.",
        "green",
        False,
        "Watch for system changes or re-orgs that break comparability.",
    ),
    ReadinessDimension(
        "target",
        "Target variable definition",
        "Net-revenue formula agreed and reproducible from source.",
        "amber",
        True,
        "Resolve gross vs. net, adjustments, and bad-debt treatment.",
    ),
    ReadinessDimension(
        "as_of",
        "Point-in-time (as-of) availability",
        "Reconstruct what was known at day 10/15/20 with no future leakage.",
        "amber",
        True,
        "If only end-of-month snapshots exist, mid-month state must be rebuilt.",
    ),
    ReadinessDimension(
        "features",
        "Feature inventory",
        "Candidate drivers identified and sourceable as-of the checkpoint.",
        "green",
        False,
        "Exclude any driver known only after close.",
    ),
    ReadinessDimension(
        "missing",
        "Missing values & completeness",
        "Missingness understood; the late-arriving-data pattern is known.",
        "amber",
        False,
        "Quantify silent gaps and unposted lag.",
    ),
    ReadinessDimension(
        "quality",
        "Data quality & consistency",
        "Formats, units, and facility codes consistent over time.",
        "green",
        False,
        "Watch facility re-coding, unit drift, and duplicates.",
    ),
    ReadinessDimension(
        "labels",
        "Label availability",
        "Actual net-revenue labels exist and join to each history period.",
        "amber",
        True,
        "No reliable actuals means nothing to train or evaluate against.",
    ),
    ReadinessDimension(
        "governance",
        "Governance, access & privacy",
        "Permissions, PHI/PII handling, and access path confirmed.",
        "green",
        False,
        "Aggregate-only data avoids PHI concerns; confirm access early.",
    ),
]


def get_metric_targets() -> list[MetricTarget]:
    """Return the per-checkpoint accuracy targets."""
    return list(_METRIC_TARGETS)


def get_success_criteria() -> list[SuccessCriterion]:
    """Return business KPIs and adoption gates that define POC success."""
    return list(_SUCCESS_CRITERIA)


def get_readiness_dimensions() -> list[ReadinessDimension]:
    """Return the data-readiness dimensions (RAG-rated; some are gates)."""
    return list(_READINESS)


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


# ---------------------------------------------------------------------------
# Guided "Build & Learn" walkthrough: teaches the data-science lifecycle by
# doing it, one step at a time. Each step names the concept, says what we do
# and why, performs a real action (mapped to an API call by ``action``), and
# tells the learner how to read the result.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WalkthroughStep:
    """One step of the guided, learn-by-building experience."""

    key: str
    number: int
    phase: str  # DS lifecycle phase, e.g. "Frame", "Data", "Model", "Evaluate"
    title: str
    goal: str
    concept: str  # the "why" — the data-science principle being taught
    what_we_do: str  # what the app does in this step
    interpret: str  # how to read the result / what to look for
    action: str  # frontend action id: none|explore|target|leakage|split|features|train|evaluate|select|explain|deliver
    lesson_key: str | None = None


_WALKTHROUGH: list[WalkthroughStep] = [
    WalkthroughStep(
        key="frame",
        number=1,
        phase="Frame",
        title="Frame the problem before touching data",
        goal="Agree what we predict, at what grain, and why it is decision support.",
        concept=(
            "Every data-science project starts by framing, not modelling. We "
            "state the prediction, its grain, the as-of moment, who acts on it, "
            "and what 'good' means. Here: predict month-end NET revenue per "
            "facility, as of a mid-month snapshot, so finance can act before "
            "close. The target is only known after accounting close - which is "
            "exactly why an early estimate is valuable. Framing prevents the "
            "most common failure: an ambiguous target."
        ),
        what_we_do="Show the resolved problem definition and configuration for this environment.",
        interpret=(
            "Note the grain (facility x accounting month x snapshot) and that "
            "net revenue != billed charges. Everything downstream honours this "
            "framing."
        ),
        action="none",
        lesson_key="problem_framing",
    ),
    WalkthroughStep(
        key="explore",
        number=2,
        phase="Data",
        title="Explore the data and get a feel for it",
        goal="Look at scale, seasonality, and how facilities differ.",
        concept=(
            "Before modelling, look. Exploratory data analysis builds intuition "
            "and surfaces problems early. Revenue has seasonality, trend, and "
            "big scale differences between facilities - a model must handle all "
            "three. We plot one facility's actual month-end net revenue over "
            "time and summarise the dataset."
        ),
        what_we_do="Load the synthetic dataset and chart a facility's monthly net-revenue history.",
        interpret=(
            "Switch facilities: some are larger, some more seasonal. That "
            "variety is why we will pool facilities into one model with facility "
            "features rather than fit one model per facility."
        ),
        action="explore",
        lesson_key="problem_framing",
    ),
    WalkthroughStep(
        key="clean",
        number=0,
        phase="Data",
        title="Clean the data: missingness and outliers",
        goal="Understand data-quality issues before modelling.",
        concept=(
            "Real revenue-cycle extracts have gaps and extremes: some measures "
            "are unposted mid-month, and a few facility-months carry unusually "
            "large charges. Data cleaning is where you decide how to handle "
            "these. We impute missing numeric values with the MEDIAN learned on "
            "the training split only (robust to skew, and leakage-safe), guard "
            "ratio features against divide-by-zero, and let tree models absorb "
            "outliers rather than deleting rows."
        ),
        what_we_do="Summarise missingness per column and flag extreme outliers, with the handling strategy.",
        interpret=(
            "Note which columns have gaps and that the fix is fit on training "
            "data only. Cleaning choices are modelling choices - document them."
        ),
        action="clean",
        lesson_key="leakage_safety",
    ),
    WalkthroughStep(
        key="eda",
        number=0,
        phase="Data",
        title="EDA: correlation and skewness",
        goal="See which drivers relate to the target, and how skewed they are.",
        concept=(
            "Exploratory data analysis quantifies relationships. Correlation "
            "with the target hints at which features carry signal (volume, gross "
            "charges, prior net revenue tend to lead). Skewness tells you a "
            "distribution has a long tail - which is why we prefer robust "
            "statistics (median) and dollar-weighted metrics (WAPE) over "
            "mean-sensitive ones. Correlation is not causation, and it does not "
            "replace leakage checks - a feature can correlate yet be forbidden."
        ),
        what_we_do="Rank features by absolute correlation with the target and report the most skewed columns.",
        interpret=(
            "Strong, sensible correlations build confidence; a surprising one "
            "may signal leakage or a data issue. High skew argues for robust "
            "handling downstream."
        ),
        action="eda",
        lesson_key="billing_vs_net_revenue",
    ),
    WalkthroughStep(
        key="target",
        number=3,
        phase="Data",
        title="Understand the target: billing is not net revenue",
        goal="See why summing charges over-predicts the real number.",
        concept=(
            "The target must be understood, not assumed. Gross (billed) charges "
            "overstate what a hospital collects. NET revenue subtracts "
            "contractual adjustments, denials, bad debt, and charity care. A "
            "naive 'sum of month-to-date charges' is therefore a biased "
            "estimator - useful only as a baseline to beat."
        ),
        what_we_do="Compare month-to-date gross charges to actual net revenue for sampled facility-months.",
        interpret=(
            "The gross-to-net ratio sits well above 1. The gap is what the "
            "model must learn - driven by payer mix, denials, and adjustments."
        ),
        action="target",
        lesson_key="billing_vs_net_revenue",
    ),
    WalkthroughStep(
        key="leakage",
        number=4,
        phase="Data",
        title="Prevent leakage: think 'as of' the snapshot",
        goal="Learn which fields are forbidden as inputs and why.",
        concept=(
            "Leakage - using information a real prediction could not have - is "
            "the number-one cause of models that look great offline and fail in "
            "production. A feature for a day-15 snapshot may only use what was "
            "known by day 15. Post-close fields (final adjustments, the target "
            "itself) are forbidden inputs. We enforce this with data contracts "
            "that fail loudly."
        ),
        what_we_do="List the forbidden (post-close) columns and the as-of rules the contracts enforce.",
        interpret=(
            "If any forbidden column reached the model, evaluation would be "
            "optimistic and wrong. The contract is your safety net."
        ),
        action="leakage",
        lesson_key="leakage_safety",
    ),
    WalkthroughStep(
        key="split",
        number=5,
        phase="Data",
        title="Split by time, never by random rows",
        goal="See the train / validation / test blocks laid out by month.",
        concept=(
            "How you split decides whether your metrics are trustworthy. Random "
            "row splitting mixes future and past and leaks information. Instead "
            "we split by accounting month: the most recent months are the test "
            "block, the block before is validation, and everything earlier is "
            "training. All snapshots of a facility-month stay together."
        ),
        what_we_do="Compute the blocked temporal split and show which months fall in each set.",
        interpret=(
            "Confirm the test months are the most recent and never overlap "
            "training. This mirrors reality: train on the past, predict the "
            "future."
        ),
        action="split",
        lesson_key="leakage_safety",
    ),
    WalkthroughStep(
        key="features",
        number=6,
        phase="Features",
        title="Engineer leakage-safe features (fit on train only)",
        goal="See raw columns become model-ready features without leaking.",
        concept=(
            "Feature engineering turns raw flash-report columns into signal: "
            "ratios (collection, denial, adjustment), run-rate, fraction of "
            "month elapsed, and one-hot categoricals. Critically, imputation "
            "statistics and encoder categories are learned on the TRAINING data "
            "only, then applied to validation/test - so the future never leaks "
            "into the past through preprocessing."
        ),
        what_we_do="Fit the leakage-safe feature builder on the training split and show the engineered feature set.",
        interpret=(
            "Compare the raw input columns to the derived features. The builder "
            "adds ratios and calendar signal a tree or linear model can use."
        ),
        action="features",
        lesson_key="automl_vs_code_first",
    ),
    WalkthroughStep(
        key="baselines",
        number=7,
        phase="Model",
        title="Establish baselines first",
        goal="Set the bar with simple, strong baselines.",
        concept=(
            "Always beat a baseline. A prior-month naive and a seasonal (same "
            "month last year) baseline are simple, strong, and free. If a "
            "complex model cannot beat them, the complexity is not earning its "
            "place - and on small data, sometimes it genuinely cannot. That is "
            "a real, useful result, not a failure of the exercise."
        ),
        what_we_do="Train all candidates and highlight how the baselines score.",
        interpret=(
            "Look at the baseline WAPE. Every learned model is judged against "
            "it. A tiny improvement over a naive baseline may not be worth the "
            "added complexity."
        ),
        action="train",
        lesson_key="automl_vs_code_first",
    ),
    WalkthroughStep(
        key="models",
        number=8,
        phase="Model",
        title="Train the code-first candidates",
        goal="Fit regularised linear and gradient-boosted models.",
        concept=(
            "Net-revenue prediction from a snapshot is structured regression, so "
            "our candidates are an elastic-net (regularised linear) and "
            "gradient-boosted trees (histogram GBM, XGBoost) - not a deep "
            "sequence model by default. One pooled model with facility features "
            "generalises better than one model per facility on limited history."
        ),
        what_we_do="Show the full ranking of every candidate on the held-out test block.",
        interpret=(
            "Scan the table: which family wins here, and by how much over the "
            "baselines? With more data, trees usually pull ahead."
        ),
        action="train",
        lesson_key="automl_vs_code_first",
    ),
    WalkthroughStep(
        key="optimize",
        number=0,
        phase="Model",
        title="Optimize: tune the hyperparameters",
        goal="Improve the best model by searching its settings.",
        concept=(
            "A model's defaults are rarely optimal. Hyperparameter tuning "
            "searches settings (here, the learning rate of gradient boosting) "
            "and keeps the one that scores best on held-out data - never on the "
            "training data, or you would overfit. Azure AutoML automates exactly "
            "this search across models and settings; here we do a small, "
            "transparent sweep so you can see the mechanism."
        ),
        what_we_do="Train gradient boosting at several learning rates and compare test-block WAPE.",
        interpret=(
            "Lower WAPE is better. Notice the metric changes with the setting - "
            "and that gains are often modest, so tune deliberately, not endlessly."
        ),
        action="optimize",
        lesson_key="automl_vs_code_first",
    ),
    WalkthroughStep(
        key="evaluate",
        number=9,
        phase="Evaluate",
        title="Evaluate with the right metric, disaggregated",
        goal="Read WAPE and bias overall, by facility, and by snapshot day.",
        concept=(
            "Pick a metric that matches the decision. For revenue we lead with "
            "WAPE (dollar-weighted) so a few tiny facilities cannot dominate the "
            "score the way they can with MAPE, and we report signed BIAS so we "
            "know if we systematically over- or under-forecast. Then we "
            "disaggregate: accuracy by facility (who is weak?) and by snapshot "
            "day (does it improve as the month fills in?)."
        ),
        what_we_do="Show WAPE/bias by snapshot day and by facility for the champion.",
        interpret=(
            "Error should shrink toward month-end as more is known. A facility "
            "with persistently high WAPE needs investigation, not a global tweak."
        ),
        action="evaluate",
        lesson_key="problem_framing",
    ),
    WalkthroughStep(
        key="select",
        number=10,
        phase="Evaluate",
        title="Select a champion (and a challenger)",
        goal="Choose the deployable model under a promotion rule.",
        concept=(
            "Model selection is a governed decision, not just 'lowest error'. "
            "The champion is best on the test block by the primary metric; the "
            "challenger is the runner-up (or, during retraining, a new "
            "candidate). A challenger is promotable only if it beats the "
            "incumbent by a configured margin - which prevents chasing noise."
        ),
        what_we_do="Show the selected champion, the challenger, and whether promotion is justified.",
        interpret=(
            "If the challenger is not 'promotable', the margin guard is doing "
            "its job: do not switch models on a coin-flip difference."
        ),
        action="select",
        lesson_key="governance",
    ),
    WalkthroughStep(
        key="explain",
        number=11,
        phase="Explain",
        title="Explain the model to earn trust",
        goal="See which features drive the predictions.",
        concept=(
            "A number finance will not trust is a number finance will not use. "
            "Permutation importance - measured on the held-out set - shows which "
            "features most affect accuracy. Explainability is both a trust tool "
            "and a debugging tool: a nonsensical top driver often reveals a data "
            "or leakage problem."
        ),
        what_we_do="Compute permutation importance for the champion on the test set.",
        interpret=(
            "Do the top drivers make business sense (volume, gross charges, "
            "prior net revenue, payer mix)? If something odd ranks first, "
            "investigate before trusting the model."
        ),
        action="explain",
        lesson_key="governance",
    ),
    WalkthroughStep(
        key="predict",
        number=12,
        phase="Serve",
        title="Run inference: score a live checkpoint",
        goal="Use the champion to predict month-end net revenue from a partial-month snapshot.",
        concept=(
            "This is what the model is FOR. In production we train occasionally "
            "but score repeatedly: at each intra-month checkpoint (say day 15) we "
            "feed the champion the as-of snapshot - only what was known by that "
            "day - and it returns predicted month-end net revenue per facility, "
            "without retraining. Every prediction is self-describing: it carries "
            "the model version, run id, cutoff day, and scoring timestamp, so any "
            "number in a report is traceable to the exact model that produced it. "
            "The full production runbook is in "
            "docs/operations/inference-in-production.md."
        ),
        what_we_do=(
            "Score the held-out test snapshots at the demo cutoff day with the "
            "champion, exactly as a production batch job would, and show the "
            "prediction rows next to the eventual actuals."
        ),
        interpret=(
            "Read a row as finance would: predicted net revenue for a facility, "
            "as of the cutoff, with its model version/run id. The predicted-vs-"
            "actual gap here is the error you would have seen scoring live - and "
            "in production the actual is only known later, after close."
        ),
        action="predict",
        lesson_key="governance",
    ),
    WalkthroughStep(
        key="retrain",
        number=0,
        phase="Operate",
        title="Monitor and retrain",
        goal="Keep the model trustworthy as the world changes.",
        concept=(
            "A deployed model decays. Inputs drift (payer mix, coding, volume), "
            "and accuracy degrades. We monitor input and prediction drift with a "
            "measure like PSI and watch post-close error. Retraining is NOT "
            "continuous: it runs on an approved schedule or on a trigger (drift, "
            "degradation, schema change, upstream-data change). Retraining "
            "re-enters this exact lifecycle - which is why a model is a product "
            "you operate, not a one-off deliverable."
        ),
        what_we_do="Review the drift signals and the retraining triggers that send us back to training.",
        interpret=(
            "Scoring runs many times per month with a fixed champion; retraining "
            "is a deliberate, governed event - not something that happens on "
            "every prediction."
        ),
        action="retrain",
        lesson_key="security_infra",
    ),
    WalkthroughStep(
        key="deliver",
        number=13,
        phase="Deliver",
        title="Deliver responsibly: govern, ship, monitor, retrain",
        goal="Turn a good model into a trustworthy, operated product.",
        concept=(
            "Building the model is the middle of the lifecycle, not the end. "
            "Responsible delivery means: register the model with lineage, "
            "review disaggregated accuracy and Responsible AI, ship via batch "
            "(or an optional online endpoint), write predictions to OneLake for "
            "Power BI, then monitor drift and retrain on a schedule or on "
            "trigger. Every prediction carries its model version and run id so "
            "it is auditable."
        ),
        what_we_do="Walk the delivery checklist that follows a validated model.",
        interpret=(
            "Notice the loop: monitoring feeds retraining, which re-enters this "
            "same lifecycle. A model is a product you operate, not a file you "
            "hand off."
        ),
        action="deliver",
        lesson_key="security_infra",
    ),
]


def get_walkthrough() -> list[WalkthroughStep]:
    """Return the ordered guided walkthrough steps (numbered by position)."""
    return [replace(step, number=i + 1) for i, step in enumerate(_WALKTHROUGH)]
