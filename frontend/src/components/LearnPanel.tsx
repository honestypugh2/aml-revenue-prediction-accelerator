import type { Area } from "../api/types";
import { useContextualNotes } from "../api/client.ts";

// The persistent, in-context learning panel. It re-queries whenever the active
// area changes, so relevant guidance follows the learner across the whole app.
type LearnPanelProps = {
  area: Area;
  isOpen: boolean;
  onToggle: () => void;
};

export function LearnPanel({ area, isOpen, onToggle }: LearnPanelProps) {
  const { data: notes, isLoading, isError } = useContextualNotes(area);

  return (
    <aside className={`learn-panel${isOpen ? " is-open" : ""}`} aria-label="Contextual learning">
      <button
        className="learn-panel__toggle"
        type="button"
        aria-expanded={isOpen}
        aria-controls="contextual-learning-content"
        onClick={onToggle}
      >
        <span className="learn-panel__toggle-icon" aria-hidden="true">
          {isOpen ? "›" : "‹"}
        </span>
        <span>{isOpen ? "Close" : "Learn"}</span>
      </button>

      <div id="contextual-learning-content" className="learn-panel__content" hidden={!isOpen}>
        <div className="learn-panel__header">
          <span className="learn-panel__badge">Learn</span>
          <div>
            <h2 className="learn-panel__title">Contextual learning</h2>
            <span className="learn-panel__area">{area}</span>
          </div>
        </div>

        {isLoading && <p className="muted">Loading guidance…</p>}
        {isError && <p className="muted">Guidance unavailable.</p>}

        {notes?.map((note) => (
          <div key={note.title} className="note">
            <h3 className="note__title">{note.title}</h3>
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
      </div>
    </aside>
  );
}
