import "../styles/AnswerPanel.css";

export default function AnswerPanel({ type, title, subtitle, answer, latency, cost }) {
  const ms = Math.round(latency);
  const seconds = (ms / 1000).toFixed(2);

  return (
    <div className="answer-panel">
      <div className={`answer-panel-header ${type}`}>
        <div className="answer-panel-icon">
          {type === "rag" ? "RAG" : "LLM"}
        </div>
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>

      <div className="answer-panel-body">
        <p className="answer-text">{answer}</p>
      </div>

      <div className="answer-panel-footer">
        <span className="meta-chip">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          {seconds}s
        </span>
        <span className="meta-chip">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
          </svg>
          ${cost.toFixed(6)}
        </span>
      </div>
    </div>
  );
}
