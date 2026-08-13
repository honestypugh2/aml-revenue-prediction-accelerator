import { useState } from "react";
import { useKnowledgeChecks, gradeAnswer } from "../api/client.ts";
import type { GradeResponse } from "../api/types";

export function KnowledgeChecks() {
  const { data: checks, isLoading, isError } = useKnowledgeChecks();
  const [results, setResults] = useState<Record<string, GradeResponse>>({});
  const [pending, setPending] = useState<string | null>(null);

  async function submit(key: string, chosenIndex: number) {
    setPending(key);
    try {
      const res = await gradeAnswer(key, chosenIndex);
      setResults((prev) => ({ ...prev, [key]: res }));
    } finally {
      setPending(null);
    }
  }

  const answered = Object.values(results);
  const score = answered.filter((r) => r.correct).length;

  return (
    <section>
      <h1>Knowledge checks</h1>
      <p className="lede">
        Test your understanding with server-graded questions. Aim for 4 / 5 or better.
      </p>

      {isLoading && <p className="muted">Loading questions…</p>}
      {isError && <p className="error">Failed to load questions.</p>}

      {checks && (
        <p className="score">
          Score: {score} / {checks.length}
        </p>
      )}

      <ol className="checks">
        {checks?.map((check) => {
          const result = results[check.key];
          return (
            <li key={check.key} className="check">
              <p className="check__q">{check.question}</p>
              <div className="check__options">
                {check.options.map((opt, idx) => {
                  const isChosen = result && result.correct_index === idx;
                  const cls =
                    result && idx === result.correct_index
                      ? "opt opt--correct"
                      : "opt";
                  return (
                    <button
                      key={opt}
                      className={cls}
                      disabled={Boolean(result) || pending === check.key}
                      onClick={() => submit(check.key, idx)}
                    >
                      {opt}
                      {isChosen && " ✓"}
                    </button>
                  );
                })}
              </div>
              {result && (
                <p className={result.correct ? "feedback ok" : "feedback bad"}>
                  {result.correct ? "Correct. " : "Not quite. "}
                  {result.explanation}
                </p>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
