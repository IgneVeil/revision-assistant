import { useState, useEffect } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [documents, setDocuments] = useState<string[]>([]);
  const [docName, setDocName] = useState("");
  const [notes, setNotes] = useState("");
  const [uploadMsg, setUploadMsg] = useState("");
  const [uploading, setUploading] = useState(false);
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("medium");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [loadingQ, setLoadingQ] = useState(false);
  const [loadingM, setLoadingM] = useState(false);

  async function loadDocuments() {
    try {
      const res = await fetch(`${API}/documents`);
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch { /* backend down: leave empty */ }
  }

  useEffect(() => { loadDocuments(); }, []);

  async function deleteDocument(name: string) {
    if (!confirm(`Delete "${name}"?`)) return;
    try {
      await fetch(`${API}/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_name: name }),
      });
      if (topic === name) setTopic("");
      loadDocuments();
    } catch {
      alert("Couldn't delete. Is the backend running?");
    }
  }

  async function uploadNotes() {
    setUploading(true);
    setUploadMsg("");
    try {
      const res = await fetch(`${API}/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_name: docName, text: notes }),
      });
      const data = await res.json();
      setUploadMsg(`Saved ${data.chunks_stored} chunk(s) from "${docName}".`);
      setNotes(""); setDocName("");
      loadDocuments();
    } catch {
      setUploadMsg("Something went wrong. Is the backend running?");
    } finally { setUploading(false); }
  }

  async function getQuestion() {
    setLoadingQ(true); setQuestion(""); setAnswer(""); setFeedback(""); setSources([]);
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
    } finally { setLoadingQ(false); }
  }

  async function submitAnswer() {
    setLoadingM(true); setFeedback(""); setSources([]);
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
    } finally { setLoadingM(false); }
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>Your notes</h2>
        {documents.length === 0 && <p className="empty">No notes yet.</p>}
        {documents.map((d) => (
          <div key={d} className={`note-item ${topic === d ? "active" : ""}`}>
            <span onClick={() => setTopic(d)} style={{ cursor: "pointer", flex: 1 }}>{d}</span>
            <span
              onClick={() => deleteDocument(d)}
              style={{ cursor: "pointer", marginLeft: 8, opacity: 0.6 }}
              title="Delete"
            >
              ✕
            </span>
          </div>
        ))}
      </aside>

      <main className="main">
        <div className="container">
          <h1>Revision Assistant</h1>
          <p className="subtitle">Add your notes, then generate and answer practice questions grounded in them.</p>

          <div className="card">
            <h2>1. Add your notes</h2>
            <label>Title</label>
            <input value={docName} onChange={(e) => setDocName(e.target.value)} placeholder="e.g. Biology Ch3" />
            <label>Notes</label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Paste your notes here..." rows={5} />
            <button onClick={uploadNotes} disabled={uploading || !docName || !notes}>
              {uploading ? "Saving..." : "Save notes"}
            </button>
            {uploadMsg && <p className="msg">{uploadMsg}</p>}
          </div>

          <div className="card">
            <h2>2. Practice</h2>
            <div className="row">
              <div>
                <label>Pick saved notes</label>
                <select value={topic} onChange={(e) => setTopic(e.target.value)}>
                  <option value="">-- select --</option>
                  {documents.map((d) => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label>Difficulty</label>
                <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                  <option value="easy">easy</option>
                  <option value="medium">medium</option>
                  <option value="hard">hard</option>
                </select>
              </div>
            </div>
            <label>Or type a topic</label>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g. photosynthesis" />
            <button onClick={getQuestion} disabled={loadingQ || !topic}>
              {loadingQ ? "Thinking..." : "Generate question"}
            </button>

            {question && (
              <div style={{ marginTop: 20 }}>
                <div className="question-box">{question}</div>
                <label style={{ marginTop: 16 }}>Your answer</label>
                <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Type your answer..." rows={4} />
                <button onClick={submitAnswer} disabled={loadingM || !answer}>
                  {loadingM ? "Marking..." : "Submit answer"}
                </button>
              </div>
            )}

            {feedback && <div className="feedback-box">{feedback}</div>}

            {sources.length > 0 && (
              <div className="sources" style={{ marginTop: 20 }}>
                <h3>Sources from your notes</h3>
                {sources.map((s, i) => <div key={i} className="source-box">{s}</div>)}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;