import { useState } from "react";
import { useEnv } from "../env.tsx";
import { useConfig, useDatasetOverview, useFacilitySeries } from "../api/client.ts";
import { LineChart } from "../components/Charts.tsx";
import { Callout } from "../components/Callout.tsx";

const currency = (v: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(v);

export function Overview() {
  const { env } = useEnv();
  const config = useConfig(env);
  const overview = useDatasetOverview(env);
  const [facility, setFacility] = useState<string | undefined>(undefined);
  const activeFacility = facility ?? overview.data?.facilities[0];
  const series = useFacilitySeries(env, activeFacility);

  return (
    <section>
      <h1>Dataset overview</h1>
      <p className="lede">
        Every row is one <strong>facility · accounting month · snapshot</strong>. The target,
        month-end net revenue, is known only after close — so we estimate it early from
        within-month signal.
      </p>

      <Callout kind="warn" title="Synthetic data">
        All values are synthetic and illustrative. Review with qualified finance, data, security,
        privacy, compliance, and operational stakeholders before any production use.
      </Callout>

      {overview.isLoading && <p className="muted">Loading dataset…</p>}
      {overview.isError && <p className="error">Failed to load dataset.</p>}

      {overview.data && (
        <>
          <div className="cards">
            <div className="card">
              <div className="card__value">{overview.data.rows.toLocaleString()}</div>
              <div className="card__label">Rows</div>
            </div>
            <div className="card">
              <div className="card__value">{overview.data.facilities.length}</div>
              <div className="card__label">Facilities</div>
            </div>
            <div className="card">
              <div className="card__value">{overview.data.months.length}</div>
              <div className="card__label">Months</div>
            </div>
            <div className="card">
              <div className="card__value">{currency(overview.data.target_mean)}</div>
              <div className="card__label">Avg net revenue</div>
            </div>
          </div>

          <div className="row">
            <label className="field">
              <span>Facility</span>
              <select
                value={activeFacility}
                onChange={(e) => setFacility(e.target.value)}
              >
                {overview.data.facilities.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </select>
            </label>
            {config.data && (
              <span className="chips">
                {config.data.snapshot_days.map((d) => (
                  <span key={d} className="chip">
                    day {d}
                  </span>
                ))}
              </span>
            )}
          </div>

          <h2>Actual month-end net revenue — {activeFacility}</h2>
          {series.isLoading && <p className="muted">Loading series…</p>}
          {series.data && (
            <LineChart
              points={series.data.points.map((p) => ({
                label: p.accounting_month,
                value: p.actual_month_end_net_revenue,
              }))}
            />
          )}
        </>
      )}
    </section>
  );
}
