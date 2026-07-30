import { useLessons } from "../api/client.ts";

export function Learn() {
  const { data: lessons, isLoading, isError } = useLessons();

  return (
    <section>
      <h1>Learn</h1>
      <p className="lede">
        Original, repository-grounded lessons on the accelerator’s engineering practices. Explore in
        any order; each links to deeper docs.
      </p>

      {isLoading && <p className="muted">Loading lessons…</p>}
      {isError && <p className="error">Failed to load lessons.</p>}

      <div className="lessons">
        {lessons?.map((lesson) => (
          <details key={lesson.key} className="lesson">
            <summary>
              <span className="lesson__title">{lesson.title}</span>
              <span className="lesson__summary">{lesson.summary}</span>
            </summary>
            <p className="lesson__body">{lesson.body}</p>
            {lesson.references.length > 0 && (
              <p className="lesson__refs">References: {lesson.references.join(", ")}</p>
            )}
          </details>
        ))}
      </div>
    </section>
  );
}
