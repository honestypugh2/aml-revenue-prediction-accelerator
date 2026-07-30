import { useEnv } from "../env.tsx";
import { useTrain } from "../api/client.ts";
import { BarChart } from "../components/Charts.tsx";
import { Callout } from "../components/Callout.tsx";

const fmt = (v: number) =>
  v >= 1000 ? v.toLocaleString(undefined, { maximumFractionDigits: 0 }) : v.toFixed(4);

export function Train() {
  const { env } = useEnv();
  const train = useTrain();
  const result = train.data;

  return (
    <section>
      <h1>Train &amp; compare (code-first, offline)</h1>
      <p className="lede">
        Candidates train on a <strong>time-aware</strong> split; the champion is the best model on
        the held-out test block. Baselines run first so complexity must earn its place.
      </p>

      <button className="btn" onClick={() => train.mutate(env)} disabled={train.isPending}>
        {train.isPending ? "Training…" : `Run local training (${env})`}
      </button>

      {train.isError && <p className="error">Training failed: {String(train.error)}</p>}

      {result && (
        <>
          <Callout kind="success" title={`Champion: ${result.champion}`}>
            Selected by <strong>{result.metric.toUpperCase()}</strong>. Challenger:{" "}
            {result.challenger ?? "—"} (promotable: {String(result.challenger_promotable)}). A
            challenger is promotable only if it beats the incumbent by the configured margin.
          </Callout>

          <h2>Model comparison</h2>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>WAPE</th>
                  <th>Bias</th>
                  <th>MAE</th>
                  <th>RMSE</th>
                  <th>MAPE</th>
                  <th>R²</th>
                </tr>
              </thead>
              <tbody>
                {result.ranking.map((m) => (
                  <tr key={m.model} className={m.is_champion ? "row--champion" : ""}>
                    <td>
                      {m.model}
                      {m.is_champion && <span className="tag">champion</span>}
                    </td>
                    <td>{(m.wape * 100).toFixed(2)}%</td>
                    <td>{(m.bias * 100).toFixed(2)}%</td>
                    <td>{fmt(m.mae)}</td>
                    <td>{fmt(m.rmse)}</td>
                    <td>{(m.mape * 100).toFixed(2)}%</td>
                    <td>{m.r2.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2>WAPE by model</h2>
          <p className="muted">
            WAPE (dollar-weighted) is the headline metric for revenue — small facilities can’t
            dominate it the way they can with MAPE.
          </p>
          <BarChart
            items={result.ranking.map((m) => ({
              label: m.model.replace(/_/g, " ").slice(0, 10),
              value: m.wape,
              highlight: m.is_champion,
            }))}
          />

          <h2>Accuracy by snapshot day</h2>
          <p className="muted">Does error shrink as more of the month is known?</p>
          <BarChart
            items={result.by_snapshot_day.map((g) => ({
              label: `day ${g.group}`,
              value: g.wape,
            }))}
          />
        </>
      )}
    </section>
  );
}
