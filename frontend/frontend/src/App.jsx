import { useEffect, useState } from "react";
import "./App.css";
import Chart from "./components/Chart";

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [databaseStatus, setDatabaseStatus] = useState("checking");
  const [aiStatus, setAiStatus] = useState("checking");

  // Check backend and database health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const result = await fetch("http://127.0.0.1:8000/health");

        if (!result.ok) {
          throw new Error("Health check failed.");
        }

        const data = await result.json();

        if (data.status === "healthy" && data.database === "connected") {
          setDatabaseStatus("connected");
          setAiStatus("ready");
        } else {
          setDatabaseStatus("disconnected");
          setAiStatus("offline");
        }
      } catch (error) {
        setDatabaseStatus("disconnected");
        setAiStatus("offline");
      }
    };

    checkHealth();
  }, []);

  // Analyze the user's question using the real backend
  const handleAnalyze = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const result = await fetch("http://127.0.0.1:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      const data = await result.json();

      if (!result.ok) {
        throw new Error(
          data.detail || "Failed to analyze the question."
        );
      }

      setResponse(data);
    } catch (error) {
      setError(error.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  // Clear analysis
  const handleClear = () => {
    setQuestion("");
    setResponse(null);
    setError("");
  };

  // Format column names for display
  const formatColumnName = (column) => {
    return column
      .replace(/_/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  };

  // Format numeric values
  const formatValue = (column, value) => {
    const lowerColumn = column.toLowerCase();

    const currencyColumns = [
      "revenue",
      "spend",
      "price",
      "freight",
      "value",
    ];

    const isCurrency = currencyColumns.some((keyword) =>
      lowerColumn.includes(keyword)
    );

    if (isCurrency && value !== null && value !== undefined) {
      const numericValue = Number(value);

      if (!Number.isNaN(numericValue)) {
        return `$${numericValue.toLocaleString("en-US", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}`;
      }
    }

    if (typeof value === "number") {
      return value.toLocaleString("en-US");
    }

    return String(value ?? "");
  };

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <div className="header-content">

          <div>
            <h1>AI Data Analyst Assistant</h1>

            <p>
              Ask questions about your e-commerce data in plain English.
            </p>
          </div>

          {/* System Status */}
          <div className="status-container">

            <span className="status-badge">
              <span
                className={`status-dot ${databaseStatus === "disconnected"
                  ? "status-dot-error"
                  : ""
                  }`}
              ></span>

              {databaseStatus === "checking"
                ? "Checking Database..."
                : databaseStatus === "connected"
                  ? "Database Connected"
                  : "Database Disconnected"}
            </span>

            <span className="status-badge">
              <span
                className={`status-dot ${aiStatus === "offline"
                  ? "status-dot-error"
                  : ""
                  }`}
              ></span>

              {aiStatus === "checking"
                ? "Checking AI..."
                : aiStatus === "ready"
                  ? "AI Assistant Ready"
                  : "AI Assistant Offline"}
            </span>

          </div>

        </div>
      </header>

      {/* Main Content */}
      <main className="container">

        {/* Question Section */}
        <section className="query-section">

          <h2>Ask your data</h2>

          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a question about your e-commerce data..."
          />

          {/* Example Questions */}
          <div className="example-questions">

            <p>Try asking:</p>

            <button
              type="button"
              onClick={() =>
                setQuestion(
                  "What are the top 5 product categories by total revenue?"
                )
              }
            >
              Top 5 product categories by revenue
            </button>

            <button
              type="button"
              onClick={() =>
                setQuestion(
                  "Which sellers have the highest total revenue?"
                )
              }
            >
              Top sellers by revenue
            </button>

            <button
              type="button"
              onClick={() =>
                setQuestion(
                  "How many orders were delivered late?"
                )
              }
            >
              Late deliveries
            </button>

          </div>

          {/* Action Buttons */}
          <button
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze Data"}
          </button>

          <button
            type="button"
            className="clear-button"
            onClick={handleClear}
          >
            Clear
          </button>

          {/* Loading Message */}
          {loading && (
            <div className="loading-message">
              <span className="loading-spinner"></span>
              <span>Analyzing your data...</span>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <p className="error">
              {error}
            </p>
          )}

        </section>

        {/* Results */}
        {response && (
          <section className="results-section">

            {/* AI Insight */}
            <div className="section-card">

              <h2>💡 AI Insight</h2>

              <p>{response.insight}</p>

            </div>

            {/* Generated SQL */}
            <div className="section-card">

              <h2>🧾 Generated SQL</h2>

              <div className="sql-placeholder">
                {response.sql}
              </div>

            </div>

            {/* Query Results */}
            <div className="section-card">

              <h2>📋 Query Results</h2>

              {response.results &&
                response.results.length > 0 ? (

                <div className="table-container">

                  <table>

                    <thead>
                      <tr>

                        {Object.keys(response.results[0]).map(
                          (column) => (
                            <th key={column}>
                              {formatColumnName(column)}
                            </th>
                          )
                        )}

                      </tr>
                    </thead>

                    <tbody>

                      {response.results.map((row, index) => (

                        <tr key={index}>

                          {Object.entries(row).map(
                            ([column, value]) => (

                              <td key={column}>
                                {formatValue(column, value)}
                              </td>

                            )
                          )}

                        </tr>

                      ))}

                    </tbody>

                  </table>

                </div>

              ) : (

                <p>No results found.</p>

              )}

            </div>

            {/* Visualization */}
            <div className="section-card">

              <h2>📊 Visualization</h2>

              <Chart
                visualization={response.visualization}
              />

            </div>

          </section>
        )}

      </main>

    </div>
  );
}

export default App;