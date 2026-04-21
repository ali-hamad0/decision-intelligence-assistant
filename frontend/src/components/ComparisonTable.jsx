import "../styles/ComparisonTable.css";

function ConfidenceCell({ confidence }) {
  if (confidence == null) return <span className="muted">—</span>;
  return (
    <div className="confidence-wrap">
      <span className="confidence-value">{(confidence * 100).toFixed(1)}%</span>
      <div className="confidence-bar-bg">
        <div className="confidence-bar-fill" style={{ width: `${confidence * 100}%` }} />
      </div>
    </div>
  );
}

function CostCell({ cost }) {
  if (cost == null) return <span className="muted">—</span>;
  if (cost === 0) return <span className="cost-zero">$0.00 <span className="muted">(in-process)</span></span>;
  return <span>${cost.toFixed(6)}</span>;
}

export default function ComparisonTable({ mlPrediction, llmPrediction }) {
  const mlLabel  = mlPrediction?.priority  || "—";
  const llmLabel = llmPrediction?.priority || "—";
  const agree    = mlLabel.toLowerCase() === llmLabel.toLowerCase();

  return (
    <div className="comparison-card">
      <div className="comparison-header">
        <span>Comparison 2 — Priority Prediction: ML Classifier vs LLM Zero-Shot</span>
        <span className="comparison-subhead">Accuracy numbers come from notebook evaluation on the held-out test set</span>
      </div>

      <table className="comparison-table">
        <thead>
          <tr>
            <th>Model</th>
            <th>Predicted Priority</th>
            <th>Test Accuracy</th>
            <th>Confidence / Reasoning</th>
            <th>Latency</th>
            <th>Cost / call</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <div className="model-cell">
                <div className="model-icon ml">ML</div>
                <div>
                  <div className="model-name">Random Forest</div>
                  <div className="model-desc">Engineered features</div>
                </div>
              </div>
            </td>
            <td><strong>{mlLabel}</strong></td>
            <td className="mono accuracy-cell">
              ~70%
              <span className="accuracy-note">180k tickets</span>
            </td>
            <td><ConfidenceCell confidence={mlPrediction?.confidence} /></td>
            <td className="mono">{mlPrediction?.latency_ms != null ? `${mlPrediction.latency_ms} ms` : "—"}</td>
            <td><CostCell cost={0} /></td>
          </tr>

          <tr>
            <td>
              <div className="model-cell">
                <div className="model-icon llm">LLM</div>
                <div>
                  <div className="model-name">Llama 3.3 70B</div>
                  <div className="model-desc">Zero-shot via Groq</div>
                </div>
              </div>
            </td>
            <td><strong>{llmLabel}</strong></td>
            <td className="mono accuracy-cell">
              <span className="muted">Not measured</span>
              <span className="accuracy-note">cost-prohibitive on test set</span>
            </td>
            <td>
              <ConfidenceCell confidence={llmPrediction?.confidence} />
              {llmPrediction?.reasoning
                ? <p className="reasoning-text">{llmPrediction.reasoning}</p>
                : <span className="muted">—</span>}
            </td>
            <td className="mono">{llmPrediction?.latency_ms != null ? `${llmPrediction.latency_ms} ms` : "—"}</td>
            <td><CostCell cost={llmPrediction?.cost_usd} /></td>
          </tr>

          <tr className="agreement-row">
            <td colSpan={2}><strong>Agreement</strong></td>
            <td colSpan={3}>
              <span className={`agreement-badge ${agree ? "agree" : "disagree"}`}>
                {agree ? (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Both predict <strong>{mlLabel}</strong>
                  </>
                ) : (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                    Disagree — ML: <strong>{mlLabel}</strong>, LLM: <strong>{llmLabel}</strong>
                  </>
                )}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
