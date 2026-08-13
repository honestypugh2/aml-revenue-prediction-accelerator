import { useEffect, useMemo, useState, type KeyboardEvent } from "react";
import { useEnv } from "../env.tsx";
import {
  useConfig,
  useDatasetSample,
  useFeaturePreview,
  useLeakage,
  usePredict,
} from "../api/client.ts";
import { Callout } from "../components/Callout.tsx";

const currency = (v: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(v);

// Format a real column value for display, using currency for money-like columns.
function fmtValue(name: string, v: unknown): string | undefined {
  if (v == null || v === "") return undefined;
  if (typeof v === "boolean") return v ? "true" : "false";
  if (typeof v === "number") {
    const isMoney =
      /revenue|charges|adjustment|denial|amount|payment/i.test(name) &&
      !/discharge/i.test(name);
    if (isMoney) return currency(v);
    // Rates, ratios, indices, and census keep decimals; counts stay whole.
    const digits = /rate|ratio|index|occupancy|_mix|case_mix|length_of_stay|census/i.test(name)
      ? 2
      : 0;
    return new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(v);
  }
  return String(v);
}

type FieldStatus =
  | "identity"
  | "kept"
  | "enrichment"
  | "flagged"
  | "added"
  | "output";

interface Field {
  name: string;
  value?: string;
  status: FieldStatus;
}

interface Stage {
  zone: string;
  title: string;
  caption: string;
  audit: string;
  fields: Field[];
  removed?: string[];
  foot?: string;
}

const STEP_MS = 1700;

// Build the six pipeline stages from real API data (with safe fallbacks so the
// simulator always renders). Each stage is a snapshot of what the payload looks
// like at that point in the leakage-safe inference flow.
function useStages(): { stages: Stage[]; ready: boolean } {
  const { env } = useEnv();
  const config = useConfig(env);
  const leakage = useLeakage(env, true);
  const features = useFeaturePreview(env, true);
  const predict = usePredict(env, true);
  const sample = useDatasetSample(env, 1);

  const ready =
    config.isSuccess &&
    leakage.isSuccess &&
    features.isSuccess &&
    predict.isSuccess &&
    sample.isSuccess;

  const stages = useMemo<Stage[]>(() => {
    const row = predict.data?.rows?.[0];
    const raw0 = sample.data?.[0];
    const lookup = (name: string): string | undefined =>
      raw0 ? fmtValue(name, raw0[name]) : undefined;
    const cutoff = row?.snapshot_day ?? config.data?.demo_cutoff_day ?? 15;
    const facility = row?.facility_id ?? "FAC-001";
    const month = row?.accounting_month ?? "2024-05";
    const asOf = row?.snapshot_date ?? `${month}-${String(cutoff).padStart(2, "0")}`;

    const identity: Field[] = [
      { name: "facility_id", value: facility, status: "identity" },
      { name: "accounting_month", value: month, status: "identity" },
      { name: "snapshot_date", value: asOf, status: "identity" },
      { name: "snapshot_day", value: String(cutoff), status: "identity" },
    ];

    const rawCols = (features.data?.raw_columns ?? [
      "service_line_group",
      "generic_payer_group",
      "month_to_date_gross_charges",
      "month_to_date_discharges",
      "month_to_date_contractual_adjustments",
      "days_elapsed",
    ]).filter((c) => !identity.some((f) => f.name === c));

    // Reflect the customer's real feed: numeric operational/historical measures
    // are available now; categorical dimensions and mid-month net-conversion
    // drivers (payer mix, adjustments, denials) are recommended enrichments
    // still being validated.
    const isDimension = (n: string): boolean =>
      raw0 ? typeof raw0[n] === "string" : /_group$/.test(n);
    const isToValidate = (n: string): boolean =>
      /^month_to_date_/.test(n) &&
      /(contractual_adjustments|denials|bad_debt|charity|case_mix)/i.test(n);
    const recommendedCols = rawCols.filter((c) => isDimension(c) || isToValidate(c));
    const availableCols = rawCols.filter((c) => !recommendedCols.includes(c));

    const availableNow: Field[] = availableCols.slice(0, 6).map((name) => ({
      name,
      value: lookup(name),
      status: "kept",
    }));
    const recommended: Field[] = recommendedCols.slice(0, 6).map((name) => ({
      name,
      value: lookup(name),
      status: "enrichment",
    }));

    const forbidden = leakage.data?.forbidden_columns ?? [
      "final_contractual_adjustments",
      "final_denials",
      "month_end_close_flag",
    ];
    const flagged: Field[] = forbidden.slice(0, 5).map((name) => ({
      name,
      value: lookup(name),
      status: "flagged",
    }));

    const example = features.data?.example ?? {
      mtd_collection_ratio: 0.62,
      mtd_denial_ratio: 0.05,
      mtd_adjustment_ratio: 0.31,
      fraction_month_elapsed: 0.5,
      mtd_gross_run_rate: 41000,
    };
    // The genuinely engineered features are the derived ratios (they carry
    // values); operational/historical columns pass through, and dimensions are
    // one-hot encoded downstream.
    const derived: Field[] = Object.entries(example).map(([name, val]) => ({
      name,
      value: typeof val === "number" ? val.toFixed(3) : String(val),
      status: "added",
    }));
    const nRaw = features.data?.n_raw ?? rawCols.length + identity.length;
    const nEngineered = features.data?.n_engineered ?? derived.length;

    const predictedValue = row ? currency(row.predicted_month_end_net_revenue) : "—";
    const lower = row?.prediction_lower != null ? currency(row.prediction_lower) : null;
    const upper = row?.prediction_upper != null ? currency(row.prediction_upper) : null;
    const modelName = predict.data?.model_name ?? "champion";
    const modelVersion = predict.data?.model_version ?? "1";
    const runId = predict.data?.run_id ?? "local-run";
    const scoredAt = predict.data?.scored_at ?? new Date().toISOString();

    const outputFields: Field[] = [
      ...identity,
      { name: "predicted_month_end_net_revenue", value: predictedValue, status: "output" },
      ...(lower && upper
        ? [
            { name: "prediction_lower", value: lower, status: "output" as const },
            { name: "prediction_upper", value: upper, status: "output" as const },
          ]
        : []),
      { name: "model_name", value: modelName, status: "output" },
      { name: "model_version", value: modelVersion, status: "output" },
      { name: "run_id", value: runId, status: "output" },
      { name: "cutoff_day", value: String(cutoff), status: "output" },
    ];

    return [
      {
        zone: "OneLake",
        title: "Ingest snapshot",
        caption:
          "The as-of flash-report extract lands. Today the customer feed is numeric-only: volume, charges, and historical net arrive as numbers.",
        audit: `Snapshot received · ${facility} · ${month} · day ${cutoff} · numeric-only feed`,
        fields: [...identity, ...availableNow, ...recommended, ...flagged],
        foot: `Numeric-only feed: ${availableNow.length} of ${availableCols.length} numeric inputs available now. ${recommendedCols.length} recommended field(s) — categorical dimensions + mid-month net-conversion drivers (payer mix, adjustments, denials) — still need validation. ${flagged.length} post-close field(s) excluded (leakage).`,
      },
      {
        zone: "Contract & leakage gate",
        title: "Validate + drop future data",
        caption:
          "Every field is checked against the data contract. Post-close and target fields are removed so nothing from after the snapshot can leak in.",
        audit: `Leakage gate · dropped ${flagged.length} post-close field(s) · target withheld · contract OK`,
        fields: [...identity, ...availableNow, ...recommended],
        removed: Array.from(
          new Set([...flagged.map((f) => f.name), "actual_month_end_net_revenue"]),
        ),
        foot: `Kept ${nRaw} leakage-safe inputs (available now + recommended); dropped the target and post-close fields.`,
      },
      {
        zone: "Feature builder",
        title: "Engineer leakage-safe features",
        caption:
          "The transformer (fit on training data only) adds derived as-of ratios, median-imputes numerics, and one-hot encodes the dimension columns.",
        audit: `Features built · ${nEngineered} model features from ${nRaw} inputs (${derived.length} derived ratios + one-hot + imputation)`,
        fields: [...identity, ...availableNow, ...recommended, ...derived],
        foot: `${derived.length} derived ratios shown; one-hot dimensions + imputed operational/historical columns give the model ${nEngineered} features. When mid-month net drivers are missing, historical-rate proxies bridge the gross→net gap.`,
      },
      {
        zone: "Champion model",
        title: "Score with the registered champion",
        caption: "The feature vector goes to the registered champion — the same model all month, no retraining.",
        audit: `Scored · ${modelName} v${modelVersion} · run ${runId}`,
        fields: [...identity, ...derived],
        foot: `${nEngineered} features in, one prediction out.`,
      },
      {
        zone: "Predictions + lineage",
        title: "Emit a self-describing prediction",
        caption:
          "Each prediction carries its model version and run id, so any number is traceable to the exact model that produced it.",
        audit: `Prediction · ${predictedValue} for ${facility} · lineage attached`,
        fields: outputFields,
      },
      {
        zone: "Deliver",
        title: "Land for Power BI",
        caption: "Predictions are written to OneLake and read by Power BI via DirectLake — early net-revenue estimates per facility.",
        audit: `Written · Files/revenue/output · scored_at ${scoredAt.slice(0, 19)}Z · Power BI ready`,
        fields: [
          ...outputFields,
          { name: "output_path", value: "Files/revenue/output", status: "output" },
        ],
      },
    ];
  }, [config.data, leakage.data, features.data, predict.data, sample.data]);

  return { stages, ready };
}

export function Simulator() {
  const { stages, ready } = useStages();
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);

  const last = stages.length - 1;
  const active = stages[Math.min(step, last)];
  const progress = last > 0 ? (Math.min(step, last) / last) * 100 : 0;

  // Autoplay: advance one stage at a time, then stop at the end.
  useEffect(() => {
    if (!playing) return;
    if (step >= last) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setStep((s) => Math.min(s + 1, last)), STEP_MS);
    return () => clearTimeout(t);
  }, [playing, step, last]);

  const run = () => {
    setStep(0);
    setPlaying(true);
  };
  const next = () => {
    setPlaying(false);
    setStep((s) => Math.min(s + 1, last));
  };
  const prev = () => {
    setPlaying(false);
    setStep((s) => Math.max(s - 1, 0));
  };
  const reset = () => {
    setPlaying(false);
    setStep(0);
  };

  const onKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "ArrowRight" || e.key === " ") {
      e.preventDefault();
      next();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      prev();
    }
  };

  return (
    <section>
      <h1>Inference flow simulator</h1>
      <p className="lede">
        Follow one <strong>partial-month snapshot</strong> through leakage-safe scoring and lineage.
      </p>

      <Callout kind="warn" title="Synthetic data walkthrough" collapsible>
        Fields and values are synthetic and illustrative. This mirrors the
        production runbook (<code>docs/operations/inference-in-production.md</code>)
        — train once, score many times, with lineage on every row.
      </Callout>

      <Callout kind="info" title="Customer feed today: numeric-only" collapsible>
        Volume, gross charges, and historical net arrive as <strong>numbers</strong>{" "}
        now. The gross→net drivers (payer mix, contractual adjustments, denials)
        and categorical dimensions are <em>recommended enrichments still being
        validated</em> — tagged <code>recommended · validate</code> below. Until
        they land, the model bridges the gap with <strong>historical-rate
        proxies</strong>. See the feature recommendation in{" "}
        <code>docs/modeling/strategy.md</code>.
      </Callout>

      <div
        className="sim"
        tabIndex={0}
        role="group"
        aria-label="Inference flow simulator"
        onKeyDown={onKeyDown}
      >
        {/* Stage track */}
        <div className="sim-track" role="list">
          <div className="sim-track__line" aria-hidden>
            <span
              className="sim-packet"
              style={{ left: `${progress}%` }}
            />
          </div>
          {stages.map((s, i) => {
            const state = i === step ? "active" : i < step ? "done" : "todo";
            return (
              <button
                key={s.zone}
                type="button"
                role="listitem"
                className={`sim-node sim-node--${state}`}
                aria-current={i === step}
                onClick={() => {
                  setPlaying(false);
                  setStep(i);
                }}
              >
                <span className="sim-node__num">{i < step ? "✓" : i + 1}</span>
                <span className="sim-node__zone">{s.zone}</span>
                <span className="sim-node__title">{s.title}</span>
              </button>
            );
          })}
        </div>

        {/* Controls */}
        <div className="sim-controls">
          <button type="button" className="btn" onClick={run}>
            ▶ Run request
          </button>
          <button type="button" className="sim-btn" onClick={prev} disabled={step === 0}>
            ◀ Prev
          </button>
          <button type="button" className="sim-btn" onClick={next} disabled={step === last}>
            Next ▶
          </button>
          <button type="button" className="sim-btn" onClick={reset}>
            Reset
          </button>
          <label className="sim-autoplay">
            <input
              type="checkbox"
              checked={playing}
              onChange={(e) => setPlaying(e.target.checked)}
            />
            Autoplay
          </label>
          <span className="sim-counter">
            {String(Math.min(step, last) + 1).padStart(2, "0")} / {String(stages.length).padStart(2, "0")}
          </span>
          {!ready && <span className="muted sim-loading">syncing live data…</span>}
        </div>

        {/* Active stage caption */}
        <p className="sim-caption">
          <strong>{active.zone}.</strong> {active.caption}
        </p>

        {/* Two panels: payload inspector + audit trail */}
        <div className="sim-panels">
          <div className="sim-panel">
            <div className="sim-panel__head">
              Payload inspector — what the data looks like right now
            </div>
            <ul className="sim-payload">
              {active.fields.map((f) => (
                <li key={f.name} className={`sim-field sim-field--${f.status}`}>
                  <span className="sim-field__name">{f.name}</span>
                  {f.value != null && <span className="sim-field__value">{f.value}</span>}
                  {f.status === "flagged" && (
                    <span className="sim-field__tag">post-close · will drop</span>
                  )}
                  {f.status === "enrichment" && (
                    <span className="sim-field__tag">recommended · validate</span>
                  )}
                  {f.status === "added" && <span className="sim-field__tag">engineered</span>}
                </li>
              ))}
            </ul>
            {active.removed && active.removed.length > 0 && (
              <div className="sim-removed">
                Dropped at the gate:
                {active.removed.map((r) => (
                  <span key={r} className="sim-removed__chip">
                    {r}
                  </span>
                ))}
              </div>
            )}
            {active.foot && <p className="sim-foot">{active.foot}</p>}
          </div>

          <div className="sim-panel">
            <div className="sim-panel__head">
              Audit trail — writes itself as the request moves
            </div>
            <ol className="sim-audit">
              {stages.slice(0, step + 1).map((s, i) => (
                <li
                  key={s.zone}
                  className={`sim-audit__line ${i === step ? "is-latest" : ""}`}
                >
                  <span className="sim-audit__seq">{String(i + 1).padStart(2, "0")}</span>
                  <span className="sim-audit__msg">{s.audit}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </section>
  );
}
