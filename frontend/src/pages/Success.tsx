import { useSuccessCriteria } from "../api/client.ts";
import { Callout } from "../components/Callout.tsx";

export function Success() {
  const { data, isLoading, isError } = useSuccessCriteria();

  const kpis = data?.criteria.filter((c) => c.category === "Business KPI") ?? [];
  const gates = data?.criteria.filter((c) => c.category === "Adoption gate") ?? [];

  return (
    <section>
      <h1>Success criteria</h1>
      <p className="lede">
        Define success across <strong>business impact</strong>, model quality, and adoption. Treat
        these targets as working defaults to validate.
      </p>

      {isLoading && <p className="muted">Loading success criteria…</p>}
      {isError && <p className="error">Failed to load success criteria.</p>}

      {data && (
        <>
          <Callout kind="success" title="The headline number this POC is judged on">
            {data.headline}
          </Callout>

          <h2 className="sc-h2">Model accuracy targets (per checkpoint)</h2>
          <p className="muted sc-note">
            WAPE (dollar-weighted) is recommended over MAPE so a few small facilities can&apos;t
            dominate the score. Bias is tracked alongside it.
          </p>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Checkpoint</th>
                  <th>Primary metric</th>
                  <th>Working target</th>
                  <th>Must beat</th>
                </tr>
              </thead>
              <tbody>
                {data.metric_targets.map((t) => (
                  <tr key={t.checkpoint}>
                    <td>{t.checkpoint}</td>
                    <td>{t.primary_metric}</td>
                    <td>{t.target}</td>
                    <td>{t.must_beat}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="sc-cols">
            <div>
              <h2 className="sc-h2">Business KPIs — what we&apos;re moving</h2>
              <ul className="sc-list">
                {kpis.map((c) => (
                  <li key={c.name} className="sc-item">
                    <span className="sc-item__name">{c.name}</span>
                    <span className="sc-item__target">{c.target}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="sc-h2">Adoption gates — what makes it real</h2>
              <ul className="sc-list">
                {gates.map((c) => (
                  <li key={c.name} className="sc-item">
                    <span className="sc-item__name">{c.name}</span>
                    <span className="sc-item__target">{c.target}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <Callout kind="info" title="A model that is accurate but unused fails">
            A model that is used but biased is dangerous. The bridge between the two is{" "}
            <strong>trust</strong>: usable in the finance workflow, explainable drivers, and a
            shadow period before anyone bets a decision on it.
          </Callout>
        </>
      )}
    </section>
  );
}
