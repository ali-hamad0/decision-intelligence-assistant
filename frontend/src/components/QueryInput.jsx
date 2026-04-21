import { useState } from "react";
import "../styles/QueryInput.css";

const EXAMPLES = [
  "My account has been locked and I cannot login",
  "App keeps crashing every time I open it",
  "How do I change my billing address?",
  "I was charged twice for my last order",
];

export default function QueryInput({ onSubmit, loading }) {
  const [text, setText] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (text.trim()) onSubmit(text.trim());
  }

  function fillExample(ex) {
    setText(ex);
  }

  return (
    <div className="query-card">
      <p className="query-card-title">Support Ticket</p>

      <div className="examples">
        <span className="examples-label">Try an example:</span>
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            className="example-chip"
            onClick={() => fillExample(ex)}
            disabled={loading}
          >
            {ex.length > 42 ? ex.slice(0, 42) + "…" : ex}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="textarea-wrap">
          <textarea
            className="query-textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Describe the support issue…"
            disabled={loading}
            rows={4}
          />
        </div>
        <p className="char-count">{text.length} characters</p>

        <div className="query-actions">
          <button
            type="submit"
            className="submit-btn"
            disabled={loading || !text.trim()}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Analyzing…
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                Analyze
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
