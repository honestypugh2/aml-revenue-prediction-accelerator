import { useMemo, useState } from "react";
import { useEnv } from "../env.tsx";
import {
  useCleaning,
  useConfig,
  useDatasetOverview,
  useEda,
  useExplain,
  useFacilitySeries,
  useFeaturePreview,
  useLeakage,
  useOptimize,
  usePredict,
  useSplitPreview,
  useTargetPreview,
  useTraining,
  useWalkthrough,
} from "../api/client.ts";
import { BarChart, LineChart } from "../components/Charts.tsx";
import { Callout } from "../components/Callout.tsx";
import { useRouter } from "../router.tsx";
import type { WalkthroughStep } from "../api/types";

const money = (v: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(v);
const pct = (v: number) => `${(v * 100).toFixed(2)}%`;

export function Build() {
  const { data: steps } = useWalkthrough();
  const [idx, setIdx] = useState(0);

  if (!steps || steps.length === 0) {
    return (
      <section>
        <h1>Build &amp; Learn</h1>
        <p className="muted">Loading the guided walkthrough…</p>
      </section>
    );
  }

  const step = steps[idx];
  const progress = ((idx + 1) / steps.length) * 100;

  return (
    <section>
      <h1>Build &amp; Learn: build the model, learn the process</h1>
      <p className="lede">
        Build a leakage-safe revenue model step by step, with synthetic-data results at every stage.
      </p>

      <div className="wt-progress">
        <div className="wt-progress__bar" style={{ width: `${progress}%` }} />
      </div>
      <p className="wt-progress__label">
        Step {step.number} of {steps.length} · <strong>{step.phase}</strong>
      </p>

      <div className="wt">
        <ol className="wt-nav" aria-label="Walkthrough steps">
          {steps.map((s, i) => (
            <li key={s.key}>
              <button
                className={`wt-nav__item ${i === idx ? "active" : ""} ${i < idx ? "done" : ""}`}
                onClick={() => setIdx(i)}
              >
                <span className="wt-nav__n">{i < idx ? "✓" : s.number}</span>
                <span className="wt-nav__t">
                  <span className="wt-nav__phase">{s.phase}</span>
                  {s.title}
                </span>
              </button>
            </li>
          ))}
        </ol>

        <div className="wt-main">
          <StepCard step={step} />
          <div className="wt-actions">
            <button className="btn ghost" disabled={idx === 0} onClick={() => setIdx((n) => n - 1)}>
              ← Previous
            </button>
            <button
              className="btn primary"
              disabled={idx === steps.length - 1}
              onClick={() => setIdx((n) => n + 1)}
            >
              {idx === steps.length - 1 ? "Done" : "Next step →"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function StepCard({ step }: { step: WalkthroughStep }) {
  return (
    <article className="wt-card">
      <header className="wt-card__head">
        <span className="wt-phase">{step.phase}</span>
        <h2>{step.title}</h2>
        <p className="wt-goal">{step.goal}</p>
      </header>

      <Callout kind="info" title="Why this matters">
        {step.concept}
      </Callout>

      <div className="wt-do">
        <h3>What we do now</h3>
        <p>{step.what_we_do}</p>
      </div>

      <div className="wt-result">
        <StepResult action={step.action} />
      </div>

      <Callout kind="success" title="How to read it">
        {step.interpret}
      </Callout>
    </article>
  );
}

function StepResult({ action }: { action: string }) {
  switch (action) {
    case "explore":
      return <ExploreResult />;
    case "clean":
      return <CleanResult />;
    case "eda":
      return <EdaResult />;
    case "target":
      return <TargetResult />;
    case "leakage":
      return <LeakageResult />;
    case "split":
      return <SplitResult />;
    case "features":
      return <FeaturesResult />;
    case "train":
      return <TrainResult />;
    case "optimize":
      return <OptimizeResult />;
    case "evaluate":
      return <EvaluateResult />;
    case "select":
      return <SelectResult />;
    case "explain":
      return <ExplainResult />;
    case "predict":
      return <PredictResult />;
    case "retrain":
      return <RetrainResult />;
    case "deliver":
      return <DeliverResult />;
    default:
      return <FrameResult />;
  }
}

function FrameResult() {
  const { env } = useEnv();
  const { data } = useConfig(env);
  if (!data) return <p className="muted">Loading configuration…</p>;
  return (
    <div className="kv">
      <div><span>Environment</span><b>{data.environment}</b></div>
      <div><span>Grain</span><b>facility × accounting month × snapshot</b></div>
      <div><span>Target</span><b>actual_month_end_net_revenue (known after close)</b></div>
      <div><span>Facilities</span><b>{data.facilities}</b></div>
      <div><span>Months of history</span><b>{data.months}</b></div>
      <div><span>Snapshot days</span><b>{data.snapshot_days.join(", ")}</b></div>
      <div><span>Primary metric</span><b>{data.primary_metric.toUpperCase()}</b></div>
    </div>
  );
}

function ExploreResult() {
  const { env } = useEnv();
  const overview = useDatasetOverview(env);
  const [facility, setFacility] = useState<string | undefined>(undefined);
  const active = facility ?? overview.data?.facilities[0];
  const series = useFacilitySeries(env, active);
  if (!overview.data) return <p className="muted">Loading dataset…</p>;
  return (
    <>
      <div className="cards">
        <div className="card"><div className="card__value">{overview.data.rows.toLocaleString()}</div><div className="card__label">Rows</div></div>
        <div className="card"><div className="card__value">{overview.data.facilities.length}</div><div className="card__label">Facilities</div></div>
        <div className="card"><div className="card__value">{overview.data.months.length}</div><div className="card__label">Months</div></div>
        <div className="card"><div className="card__value">{money(overview.data.target_mean)}</div><div className="card__label">Avg net revenue</div></div>
      </div>
      <label className="field" style={{ maxWidth: 220 }}>
        <span>Facility</span>
        <select value={active} onChange={(e) => setFacility(e.target.value)}>
          {overview.data.facilities.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
      </label>
      {series.data && (
        <LineChart points={series.data.points.map((p) => ({ label: p.accounting_month, value: p.actual_month_end_net_revenue }))} />
      )}
    </>
  );
}

function TargetResult() {
  const { env } = useEnv();
  const { data } = useTargetPreview(env, true);
  if (!data) return <p className="muted">Comparing gross charges to net revenue…</p>;
  return (
    <>
      <p>
        Average gross-to-net ratio at the demo cutoff:{" "}
        <b>{data.average_gross_to_net_ratio.toFixed(2)}×</b> — billed charges are far above what is
        actually collected.
      </p>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Facility</th><th>Month</th><th>MTD gross charges</th><th>Actual net revenue</th><th>Gross ÷ Net</th></tr></thead>
          <tbody>
            {data.items.map((it) => (
              <tr key={`${it.facility_id}-${it.accounting_month}`}>
                <td>{it.facility_id}</td>
                <td>{it.accounting_month}</td>
                <td>{money(it.gross_charges)}</td>
                <td>{money(it.net_revenue)}</td>
                <td>{it.gross_to_net_ratio.toFixed(2)}×</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function LeakageResult() {
  const { env } = useEnv();
  const { data } = useLeakage(env, true);
  if (!data) return <p className="muted">Loading leakage rules…</p>;
  return (
    <div className="g2-cols">
      <div>
        <h4>Forbidden as inputs (post-close)</h4>
        <ul className="tight">{data.forbidden_columns.map((c) => <li key={c}><code>{c}</code></li>)}</ul>
      </div>
      <div>
        <h4>As-of rules the contracts enforce</h4>
        <ul className="tight">{data.rules.map((r) => <li key={r}>{r}</li>)}</ul>
      </div>
    </div>
  );
}

function SplitResult() {
  const { env } = useEnv();
  const { data } = useSplitPreview(env, true);
  if (!data) return <p className="muted">Computing the temporal split…</p>;
  const cell = (m: string, kind: string) => (
    <span key={m} className={`mo mo--${kind}`} title={`${m} (${kind})`}>{m.slice(2)}</span>
  );
  return (
    <>
      <div className="mo-timeline">
        {data.train_months.map((m) => cell(m, "train"))}
        {data.validation_months.map((m) => cell(m, "val"))}
        {data.test_months.map((m) => cell(m, "test"))}
      </div>
      <div className="legend">
        <span><i style={{ background: "#3b5b9a" }} /> Train ({data.train_rows} rows)</span>
        <span><i style={{ background: "#e9a100" }} /> Validation ({data.validation_rows})</span>
        <span><i style={{ background: "#34d399" }} /> Test ({data.test_rows})</span>
      </div>
      <p className="muted">Train on the past → validate → test on the most recent months. No overlap, no random rows.</p>
    </>
  );
}

function FeaturesResult() {
  const { env } = useEnv();
  const { data } = useFeaturePreview(env, true);
  if (!data) return <p className="muted">Fitting the leakage-safe feature builder on the training split…</p>;
  return (
    <>
      <p>
        The builder turned <b>{data.n_raw}</b> raw columns into <b>{data.n_engineered}</b> model-ready
        features (imputation + one-hot categories learned on training data only).
      </p>
      <h4>Example derived features (first training row)</h4>
      <div className="kv">
        {Object.entries(data.example).map(([k, v]) => (
          <div key={k}><span>{k}</span><b>{v}</b></div>
        ))}
      </div>
      <details className="ref">
        <summary>See all engineered feature names</summary>
        <div className="chips" style={{ padding: "10px 0" }}>
          {data.engineered_features.map((f) => <span key={f} className="chip">{f}</span>)}
        </div>
      </details>
    </>
  );
}

function useSharedTraining() {
  const { env } = useEnv();
  return useTraining(env, true);
}

function TrainResult() {
  const { data, isLoading } = useSharedTraining();
  if (isLoading || !data) return <p className="muted">Training all candidates on the time-aware split…</p>;
  return (
    <>
      <p>Champion by <b>{data.metric.toUpperCase()}</b>: <b>{data.champion}</b></p>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Model</th><th>WAPE</th><th>Bias</th><th>MAE</th><th>R²</th></tr></thead>
          <tbody>
            {data.ranking.map((m) => (
              <tr key={m.model} className={m.is_champion ? "row--champion" : ""}>
                <td>{m.model}{m.is_champion && <span className="tag">champion</span>}{(m.model === "naive_prior" || m.model === "seasonal_naive") && <span className="tag" style={{ background: "#64748b" }}>baseline</span>}</td>
                <td>{pct(m.wape)}</td>
                <td>{pct(m.bias)}</td>
                <td>{money(m.mae)}</td>
                <td>{m.r2.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <BarChart items={data.ranking.map((m) => ({ label: m.model.replace(/_/g, " ").slice(0, 10), value: m.wape, highlight: m.is_champion }))} />
    </>
  );
}

function EvaluateResult() {
  const { data, isLoading } = useSharedTraining();
  if (isLoading || !data) return <p className="muted">Evaluating the champion…</p>;
  return (
    <>
      <h4>WAPE by snapshot day (does error shrink later in the month?)</h4>
      <BarChart items={data.by_snapshot_day.map((g) => ({ label: `day ${g.group}`, value: g.wape }))} />
      <h4>WAPE by facility (where is the model weak?)</h4>
      <BarChart items={data.by_facility.map((g) => ({ label: g.group, value: g.wape }))} />
    </>
  );
}

function SelectResult() {
  const { data, isLoading } = useSharedTraining();
  if (isLoading || !data) return <p className="muted">Selecting champion and challenger…</p>;
  return (
    <Callout kind="success" title={`Champion: ${data.champion}`}>
      Selected by {data.metric.toUpperCase()}. Challenger: <b>{data.challenger ?? "—"}</b>. Promotable
      over the incumbent by the configured margin?{" "}
      <b>{data.challenger_promotable ? "yes" : "no"}</b>. The margin guard stops us switching models on
      noise.
    </Callout>
  );
}

function ExplainResult() {
  const { env } = useEnv();
  const { data, isLoading } = useExplain(env, true);
  if (isLoading || !data) return <p className="muted">Computing permutation importance on the test set…</p>;
  return (
    <>
      <p>Drivers for <b>{data.model}</b> (permutation importance, held-out test set):</p>
      <BarChart items={data.items.map((i) => ({ label: i.feature.replace(/_/g, " ").slice(0, 14), value: Math.max(0, i.importance) }))} />
    </>
  );
}

function PredictResult() {
  const { env } = useEnv();
  const { navigate } = useRouter();
  const { data, isLoading } = usePredict(env, true);
  if (isLoading || !data)
    return <p className="muted">Scoring the held-out checkpoint with the champion…</p>;
  return (
    <>
      <Callout kind="info" title="This is a production-style batch scoring run">
        The champion scored the day-{data.cutoff_day} snapshots it never trained on. Every prediction
        carries its lineage — model <b>{data.model_name}</b> v{data.model_version}, run{" "}
        <code>{data.run_id}</code> — so any number is traceable. Checkpoint WAPE: <b>{pct(data.wape)}</b>.
      </Callout>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Facility</th>
              <th>Month</th>
              <th>As of</th>
              <th>Predicted net revenue</th>
              <th>Actual (after close)</th>
              {data.has_intervals && <th>95% interval</th>}
              <th>Abs % error</th>
            </tr>
          </thead>
          <tbody>
            {data.rows.map((r) => (
              <tr key={`${r.facility_id}-${r.accounting_month}`}>
                <td>{r.facility_id}</td>
                <td>{r.accounting_month}</td>
                <td>{r.snapshot_date}</td>
                <td>{money(r.predicted_month_end_net_revenue)}</td>
                <td>
                  {r.actual_month_end_net_revenue != null
                    ? money(r.actual_month_end_net_revenue)
                    : "—"}
                </td>
                {data.has_intervals && (
                  <td>
                    {r.prediction_lower != null && r.prediction_upper != null
                      ? `${money(r.prediction_lower)} – ${money(r.prediction_upper)}`
                      : "—"}
                  </td>
                )}
                <td>{r.abs_pct_error != null ? pct(r.abs_pct_error) : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted">
        In production the “actual” column is blank until after accounting close — it is shown here
        only so you can see how accurate the live estimate was. This output row is exactly what lands
        in OneLake for Power BI.
      </p>
      <div className="row">
        <button type="button" className="btn" onClick={() => navigate("/simulator")}>
          ▶ Simulate inference step-by-step
        </button>
        <span className="muted">
          Watch one snapshot flow through the leakage gate, features, champion, and lineage.
        </span>
      </div>
    </>
  );
}

function CleanResult() {
  const { env } = useEnv();
  const { data } = useCleaning(env, true);
  if (!data) return <p className="muted">Profiling data quality…</p>;
  return (
    <>
      <p>
        <b>{data.columns_with_missing.length}</b> columns have missing values across{" "}
        {data.rows.toLocaleString()} rows. The fix is median imputation fit on the training split
        only.
      </p>
      {data.columns_with_missing.length > 0 && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr><th>Column</th><th>Missing</th><th>%</th><th>Strategy</th></tr>
            </thead>
            <tbody>
              {data.columns_with_missing.map((c) => (
                <tr key={c.column}>
                  <td>{c.column}</td>
                  <td>{c.missing_count}</td>
                  <td>{pct(c.missing_pct)}</td>
                  <td>{c.strategy}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Callout kind="info" title="Outliers">{data.outlier_note}</Callout>
    </>
  );
}

function EdaResult() {
  const { env } = useEnv();
  const { data } = useEda(env, true);
  if (!data) return <p className="muted">Computing correlations and skewness…</p>;
  return (
    <>
      <h4>Correlation with the target ({data.target})</h4>
      <BarChart
        items={data.correlations.map((c) => ({
          label: c.feature.replace(/month_to_date_/g, "").slice(0, 14),
          value: Math.abs(c.corr_with_target),
          highlight: c.corr_with_target < 0,
        }))}
      />
      <p className="muted">Bars show absolute correlation; highlighted bars are negative.</p>
      <h4>Most skewed features</h4>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr><th>Feature</th><th>Skewness</th></tr>
          </thead>
          <tbody>
            {data.skewness.slice(0, 6).map((s) => (
              <tr key={s.feature}><td>{s.feature}</td><td>{s.skewness}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted">High |skew| means a long tail — a reason we use robust stats and WAPE.</p>
    </>
  );
}

function OptimizeResult() {
  const { env } = useEnv();
  const { data, isLoading } = useOptimize(env, true);
  if (isLoading || !data) return <p className="muted">Sweeping hyperparameters…</p>;
  return (
    <>
      <p>
        Tuning <b>{data.model}</b> · <code>{data.hyperparameter}</code>. Best:{" "}
        <b>{data.best_setting}</b> (lowest WAPE).
      </p>
      <BarChart
        items={data.trials.map((t) => ({
          label: t.setting.replace("learning_rate=", "lr "),
          value: t.wape,
          highlight: t.is_best,
        }))}
      />
      <p className="muted">
        A small, transparent sweep. Azure AutoML automates this search across many models and
        settings.
      </p>
    </>
  );
}

function RetrainResult() {
  const triggers = [
    "Scheduled cadence — e.g. monthly after close, on approval.",
    "Input drift — PSI on key features (payer mix, volume, gross charges) exceeds threshold.",
    "Prediction drift — the predicted distribution shifts vs. a reference window.",
    "Accuracy degradation — post-close WAPE rises above the agreed bar.",
    "Schema / upstream change — new facilities, re-coding, or a source change.",
  ];
  return (
    <>
      <Callout kind="info" title="Scoring is frequent; retraining is deliberate">
        The champion scores at every checkpoint all month. Retraining is a governed event triggered
        by one of the signals below — it re-enters the whole lifecycle (back to training &amp;
        selection).
      </Callout>
      <ul className="tight">
        {triggers.map((t) => (
          <li key={t}>{t}</li>
        ))}
      </ul>
    </>
  );
}

function DeliverResult() {
  const items = useMemo(
    () => [
      "Register the champion in the Azure ML registry (captures lineage: job + run id).",
      "Review disaggregated accuracy and the Responsible AI checklist before promotion.",
      "Ship via batch scoring (default) or an optional managed online endpoint.",
      "Write predictions to OneLake as a flat table for a Power BI DirectLake model.",
      "Monitor input & prediction drift (PSI); alert when it shifts.",
      "Retrain on a schedule or on trigger — which re-enters this same lifecycle.",
    ],
    [],
  );
  return (
    <ul className="checklist">
      {items.map((t) => (
        <li key={t}><input type="checkbox" /> <span>{t}</span></li>
      ))}
    </ul>
  );
}
