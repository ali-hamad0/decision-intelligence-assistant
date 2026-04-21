import { useState } from "react";
import { submitCompare } from "./api/index.js";
import QueryInput from "./components/QueryInput";
import AnswerPanel from "./components/AnswerPanel";
import SourcePanel from "./components/SourcePanel";
import ComparisonTable from "./components/ComparisonTable";
import "./styles/App.css";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [result, setResult]   = useState(null);

  async function handleSubmit(text) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await submitCompare(text);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Decision Intelligence Assistant</h1>
        <p>Compare RAG vs LLM-only answers · ML vs LLM priority predictions</p>
      </header>

      <main className="app-main">
        <QueryInput onSubmit={handleSubmit} loading={loading} />

        {error && (
          <div className="error-banner">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {error}
          </div>
        )}

        {!result && !loading && !error && (
          <div className="empty-state">
            <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><polyline points="12 16 12 16"/>
            </svg>
            <h3>Enter a support ticket above</h3>
            <p>Results will show RAG vs LLM answers and ML vs LLM priority predictions side by side.</p>
          </div>
        )}

        {result && (
          <>
            <div className="answer-row">
              <AnswerPanel
                type="rag"
                title="RAG Answer"
                subtitle="Retrieved context + LLM"
                answer={result.rag.answer}
                latency={result.rag.latency_ms}
                cost={result.rag.cost_usd}
              />
              <AnswerPanel
                type="llm"
                title="LLM-only Answer"
                subtitle="No retrieval, direct generation"
                answer={result.llm.answer}
                latency={result.llm.latency_ms}
                cost={result.llm.cost_usd}
              />
            </div>

            <SourcePanel sources={result.rag.sources} lowSimilarity={result.rag.low_similarity} />

            <ComparisonTable
              mlPrediction={result.ml_prediction}
              llmPrediction={result.llm_prediction}
            />
          </>
        )}
      </main>
    </div>
  );
}
