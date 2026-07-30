import type { Area } from "../api/types";
import { useContextualNotes } from "../api/client.ts";

// The persistent, in-context learning panel. It re-queries whenever the active
// area changes, so relevant guidance follows the learner across the whole app.
export function LearnPanel({ area }: { area: Area }) {
  const { data: notes, isLoading, isError } = useContextualNotes(area);

  return (
    <aside className="learn-panel" aria-label="Contextual learning">
      <div className="learn-panel__header">
        <span className="learn-panel__badge">Learn</span>
        <span className="learn-panel__area">{area}</span>
      </div>

      {isLoading && <p className="muted">Loading guidance…</p>}
      {isError && <p className="muted">Guidance unavailable.</p>}

      {notes?.map((note) => (
        <div key={note.title} className="note">
          <h4 className="note__title">{note.title}</h4>
          <p className="note__detail">{note.detail}</p>
          {note.tip && (
            <p className="note__tip">
              <strong>Try:</strong> {note.tip}
            </p>
          )}
        </div>
      ))}

      <p className="learn-panel__footnote">
        All data is synthetic. This is decision support, not clinical or financial advice.
      </p>
    </aside>
  );
}
