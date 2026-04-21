import { useState } from "react";
import "../styles/SourcePanel.css";

function badgeClass(priority) {
  const map = { urgent: "badge-urgent", high: "badge-high", normal: "badge-normal", low: "badge-low" };
  return map[(priority || "").toLowerCase()] || "badge-unknown";
}

export default function SourcePanel({ sources, lowSimilarity }) {
  const [open, setOpen] = useState(true);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="source-panel">
      {lowSimilarity && (
        <div className="low-similarity-warning">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          Low similarity — best retrieved score &lt; 0.15. The retrieved tickets may not be relevant to this query. The RAG answer is less reliable than usual.
        </div>
      )}
      <div className="source-panel-header" onClick={() => setOpen((o) => !o)}>
        <div className="source-panel-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
          </svg>
          Retrieved Sources
          <span className="source-count-badge">{sources.length}</span>
        </div>
        <svg className={`chevron ${open ? "open" : ""}`} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </div>

      {open && (
        <div className="source-list">
          {sources.map((src, i) => {
            const score = src.similarity_score;
            const pct = Math.round(score * 100);
            return (
              <div key={i} className="source-item">
                <div className="source-item-top">
                  <span className="source-index">{i + 1}</span>
                  <p className="source-text">{src.text}</p>
                </div>
                <div className="source-item-meta">
                  <span className={`priority-badge ${badgeClass(src.priority)}`}>{src.priority}</span>
                  <div className="score-bar-wrap">
                    <div className="score-bar-bg">
                      <div className="score-bar-fill" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="score-label">{score.toFixed(3)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
