import { useState } from "react";
import { useDataReadiness } from "../api/client.ts";
import { Callout } from "../components/Callout.tsx";
import type { Rag, ReadinessDimension } from "../api/types";

const RAG_POINTS: Record<Rag, number> = { green: 2, amber: 1, red: 0 };
const RAG_LABEL: Record<Rag, string> = { green: "Ready", amber: "Gap", red: "Blocker" };

export function Readiness() {
  const { data, isLoading, isError } = useDataReadiness();
  const [overrides, setOverrides] = useState<Record<string, Rag>>({});

  const dims: ReadinessDimension[] = data ?? [];
  const ratingOf = (d: ReadinessDimension): Rag => overrides[d.key] ?? d.default_rating;

  const ratings = dims.map(ratingOf);
  const points = ratings.reduce((s, r) => s + RAG_POINTS[r], 0);
  const score = dims.length ? Math.round((points / (dims.length * 2)) * 100) : 0;
  const redCount = ratings.filter((r) => r === "red").length;
  const gateRed = dims.some((d) => d.is_gate && ratingOf(d) === "red");

  let verdict = "Not ready";
  let tone: "green" | "amber" | "red" = "red";
  if (gateRed) {
    verdict = "Not ready";
    tone = "red";
  } else if (score >= 80 && redCount === 0) {
    verdict = "Go";
    tone = "green";
  } else if (score >= 60 || redCount <= 1) {
    verdict = "Conditional go";
    tone = "amber";
  }

  return (
    <section>
      <h1>Data readiness assessment</h1>
      <p className="lede">
        Rate each dimension <strong>Green</strong> (ready), <strong>Amber</strong> (workable
        gap), or <strong>Red</strong> (blocker). The score and gate recommendation update live.
      </p>

      {isLoading && <p className="muted">Loading readiness dimensions…</p>}
      {isError && <p className="error">Failed to load readiness dimensions.</p>}

      {data && (
        <>
          <div className={`rd-score rd-score--${tone}`}>
            <div className="rd-score__value">{score}%</div>
            <div className="rd-score__meta">
              <div className={`rd-verdict rd-verdict--${tone}`}>{verdict}</div>
              <div className="rd-score__bar" aria-hidden>
                <span style={{ width: `${score}%` }} className={`rd-score__fill rd-score__fill--${tone}`} />
              </div>
              <div className="muted rd-score__legend">
                Green = 2 · Amber = 1 · Red = 0. <button className="rd-reset" onClick={() => setOverrides({})}>Reset to defaults</button>
              </div>
            </div>
          </div>

          <Callout kind="warn" title="Gate logic">
            Any <strong>Red on a gate dimension</strong> (target variable, point-in-time
            availability, or label availability) caps the recommendation at{" "}
            <strong>Not ready</strong> regardless of score — these are structural blockers for a
            supervised forecasting POC.
          </Callout>

          <ul className="rd-list">
            {dims.map((d) => {
              const current = ratingOf(d);
              return (
                <li key={d.key} className="rd-item">
                  <div className="rd-item__head">
                    <span className="rd-item__name">
                      {d.dimension}
                      {d.is_gate && <span className="rd-gate">gate</span>}
                    </span>
                    <div className="rd-rag" role="group" aria-label={`Rating for ${d.dimension}`}>
                      {(["red", "amber", "green"] as Rag[]).map((r) => (
                        <button
                          key={r}
                          type="button"
                          className={`rd-rag__btn rd-rag__btn--${r} ${current === r ? "is-on" : ""}`}
                          aria-pressed={current === r}
                          onClick={() => setOverrides((o) => ({ ...o, [d.key]: r }))}
                        >
                          {r[0].toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                  <p className="rd-item__desc">{d.description}</p>
                  {current !== "green" && <p className="rd-item__guide">{RAG_LABEL[current]} — {d.guidance}</p>}
                </li>
              );
            })}
          </ul>
        </>
      )}
    </section>
  );
}
