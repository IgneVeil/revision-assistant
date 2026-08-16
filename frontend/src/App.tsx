import { useState } from "react";

const API = "http://localhost:8000";

function App() {
  const [topic, setTopic] = useState("photosynthesis");
  const [difficulty, setDifficulty] = useState("medium");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [loadingQ, setLoadingQ] = useState(false);
  const [loadingM, setLoadingM] = useState(false);

  async function getQuestion() {
    setLoadingQ(true);
    setQuestion("");
    setAnswer("");
    setFeedback("");
    setSources([]);
    try {
      const res = await fetch(`${API}/question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, difficulty }),
      });
      const data = await res.json();
      setQuestion(data.question);
    } catch {
      setQuestion("Something went wrong. Is the backend running?");
    } finally {
      setLoadingQ(false);
    }
  }

  async function submitAnswer() {
    setLoadingM(true);
    setFeedback("");
    setSources([]);
    try {
      const res = await fetch(`${API}/mark`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, student_answer: answer, topic }),
      });
      const data = await res.json();
      setFeedback(data.feedback);
      setSources(data.sources || []);
    } catch {
      setFeedback("Something went wrong marking your answer.");
    } finally {
      setLoadingM(false);
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Revision Assistant</h1>

      <label>Topic: </label>
      <input value={topic} onChange={(e) => setTopic(e.target.value)} />

      <label> Difficulty: </label>
      <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
        <option value="easy">easy</option>
        <option value="medium">medium</option>
        <option value="hard">hard</option>
      </select>

      <br /><br />
      <button onClick={getQuestion} disabled={loadingQ}>
        {loadingQ ? "Thinking..." : "Generate question"}
      </button>

      {question && (
        <div style={{ marginTop: 20 }}>
          <p style={{ padding: 15, background: "#f0f0f0", borderRadius: 8 }}>
            {question}
          </p>

          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here..."
            rows={4}
            style={{ width: "100%", boxSizing: "border-box" }}
          />

          <br /><br />
          <button onClick={submitAnswer} disabled={loadingM || !answer}>
            {loadingM ? "Marking..." : "Submit answer"}
          </button>
        </div>
      )}

      {feedback && (
        <p style={{ marginTop: 20, padding: 15, background: "#e8f5e9", borderRadius: 8, whiteSpace: "pre-wrap" }}>
          {feedback}
        </p>
      )}

      {sources.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <h3>Sources (from your notes)</h3>
          {sources.map((s, i) => (
            <p key={i} style={{ padding: 10, background: "#fff8e1", borderRadius: 8, fontSize: 14 }}>
              {s}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;