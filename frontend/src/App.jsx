import { useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [activeTab, setActiveTab] = useState("ask");

  const [question, setQuestion] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const [answer, setAnswer] = useState("");
  const [analysis, setAnalysis] = useState("");
  const [interviewQuestions, setInterviewQuestions] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
const [resumeUploaded, setResumeUploaded] = useState(false);
const [uploadingResume, setUploadingResume] = useState(false);

  // -----------------------------
  // MOUSE GLOW
  // -----------------------------
const handleButtonMove = (e) => {
  const button = e.currentTarget;
  const rect = button.getBoundingClientRect();

  const x = e.clientX - (rect.left + rect.width / 2);
  const y = e.clientY - (rect.top + rect.height / 2);

  button.style.transform = `translate(${x * 0.18}px, ${y * 0.18}px)`;
};

const handleButtonLeave = (e) => {
  e.currentTarget.style.transform = "";
};
  const handleMouseMove = (e) => {
    document.documentElement.style.setProperty(
      "--mouse-x",
      `${e.clientX}px`
    );

    document.documentElement.style.setProperty(
      "--mouse-y",
      `${e.clientY}px`
    );
  };

  // -----------------------------
  // 3D CARD TILT
  // -----------------------------

  const handleCardMove = (e) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const rotateX = ((y / rect.height) - 0.5) * -5;
    const rotateY = ((x / rect.width) - 0.5) * 5;

    card.style.transform = `
      perspective(900px)
      rotateX(${rotateX}deg)
      rotateY(${rotateY}deg)
      translateY(-3px)
    `;
  };

  const handleCardLeave = (e) => {
    e.currentTarget.style.transform = "";
  };

  // -----------------------------
  // CLEAR RESULTS
  // -----------------------------

  const clearResults = () => {
    setAnswer("");
    setAnalysis("");
    setInterviewQuestions("");
    setError("");
  };

  // -----------------------------
  // CHANGE TAB
  // -----------------------------

  const changeTab = (tab) => {
    setActiveTab(tab);
    clearResults();
  };

  // -----------------------------
  // ASK AI
  // -----------------------------

  const askAI = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setAnswer(data.answer);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
    // -----------------------------
  // RESUME UPLOAD
  // -----------------------------

 const uploadResume = async (file) => {
  if (!file) return;

  setResumeFile(file);
  setUploadingResume(true);
  setError("");
  setResumeUploaded(false);

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/upload-resume`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.message || "Unable to upload resume.");
    }

    setResumeUploaded(true);
  } catch (err) {
    setError(err.message);
  } finally {
    setUploadingResume(false);
  }
};

  // -----------------------------
  // JOB MATCH
  // -----------------------------

  const analyzeJob = async () => {
    if (!jobDescription.trim()) return;

    setLoading(true);
    setError("");
    setAnalysis("");

    try {
      const response = await fetch(`${API_URL}/analyze-job`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: jobDescription.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to analyze the job.");
      }

      setAnalysis(data.analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------
  // INTERVIEW PREP
  // -----------------------------

  const generateInterview = async () => {
    if (!jobDescription.trim()) return;

    setLoading(true);
    setError("");
    setInterviewQuestions("");

    try {
      const response = await fetch(`${API_URL}/interview`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: jobDescription.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to generate interview questions."
        );
      }

      setInterviewQuestions(data.questions);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app" onMouseMove={handleMouseMove}>

  <div className="ambient-light light-one"></div>
  <div className="ambient-light light-two"></div>

  <div className="particles">
    {Array.from({ length: 18 }).map((_, index) => (
      <span
        key={index}
        className="particle"
        style={{
          "--i": index,
        }}
      />
    ))}
  </div>

  <aside className="sidebar"></aside>
      <aside className="sidebar">
        <div className="brand">
  <div className="brand-mark">
    <div className="brand-core">P</div>

    <span className="node node-1"></span>
    <span className="node node-2"></span>
    <span className="node node-3"></span>
  </div>

  <div className="brand-name">
    <h2>PLACEMENT<span>/</span></h2>
    <p>INTELLIGENCE</p>
  </div>
</div>

        <nav>
          <button
            className={
              activeTab === "ask" ? "nav-item active" : "nav-item"
            }
            onClick={() => changeTab("ask")}
          >
            <span>◉</span>
            Ask AI
          </button>

          <button
            className={
              activeTab === "match" ? "nav-item active" : "nav-item"
            }
            onClick={() => changeTab("match")}
          >
            <span>◈</span>
            Job Match
          </button>

          <button
            className={
              activeTab === "interview"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => changeTab("interview")}
          >
            <span>◇</span>
            Interview Prep
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot"></div>
          <span>AI system online</span>
        </div>
      </aside>

      {/* =============================
          MAIN CONTENT
      ============================= */}

      <main className="main">
        {/* TOP BAR */}

        <header className="topbar">
          <div>
            <p className="eyebrow">AI-POWERED CAREER TOOL</p>

            <h1>
              {activeTab === "ask" &&
                "Ask your resume anything."}

              {activeTab === "match" &&
                "Understand your job match."}

              {activeTab === "interview" &&
                "Prepare for your interview."}
            </h1>
          </div>

          <div className="system-badge">
            <span></span>
            RAG ACTIVE
          </div>
        </header>
        {/* RESUME UPLOAD */}

<div className="resume-upload-card">
  <div className="resume-upload-info">
    <span className="resume-upload-label">PROFILE</span>

    <h2>
      {resumeUploaded ? "Resume uploaded ✓" : "Upload your resume"}
    </h2>

    <p>
      {resumeUploaded
        ? `${resumeFile?.name} is ready for AI analysis.`
        : "Upload your PDF resume to personalize the placement assistant."}
    </p>
  </div>

  <div className="resume-upload-actions">
    <label className="primary-button">
      {uploadingResume ? "Uploading..." : "Upload Resume →"}

      <input
        type="file"
        accept=".pdf,application/pdf"
        hidden
        disabled={uploadingResume}
        onChange={(e) => {
          const file = e.target.files[0];

          if (file) {
            uploadResume(file);
          }

          e.target.value = "";
        }}
      />
    </label>
  </div>

  {resumeUploaded && (
    <div className="upload-success">
      ✓ Resume processed successfully
    </div>
  )}
</div>

        {/* =============================
            ASK AI
        ============================= */}

        {activeTab === "ask" && (
          <section className="workspace">
            <div
              className="hero-card"
              onMouseMove={handleCardMove}
              onMouseLeave={handleCardLeave}
            >
              <div className="hero-number">01</div>

              <div>
                <h2>Resume Intelligence</h2>

                <p>
                  Ask questions and get answers grounded in the
                  candidate's resume.
                </p>
              </div>
            </div>

            <div
              className="input-card"
              onMouseMove={handleCardMove}
              onMouseLeave={handleCardLeave}
            >
              <label>YOUR QUESTION</label>

              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g. What programming languages does this candidate know?"
              />

              <div className="action-row">
                <span>
                  Powered by local RAG + Llama 3.2
                </span>

                <button
  className="primary-button"
  onClick={askAI}
  onMouseMove={handleButtonMove}
  onMouseLeave={handleButtonLeave}
  disabled={
    loading || !question.trim()
  }
>
  {loading ? "Thinking..." : "Ask AI →"}
</button>
              </div>
            </div>

            {answer && (
              <div
                className="result-card"
                onMouseMove={handleCardMove}
                onMouseLeave={handleCardLeave}
              >
                <div className="result-heading">
                  <span className="result-label">
                    AI RESPONSE
                  </span>

                  <span className="check">
                    ✓ GROUNDED
                  </span>
                </div>

                <p className="answer-text">
                  {answer}
                </p>
              </div>
            )}
          </section>
        )}

        {/* =============================
            JOB MATCH
        ============================= */}

        {activeTab === "match" && (
          <section className="workspace">
            <div
              className="hero-card"
              onMouseMove={handleCardMove}
              onMouseLeave={handleCardLeave}
            >
              <div className="hero-number">02</div>

              <div>
                <h2>Job Match Analysis</h2>

                <p>
                  Compare job requirements against evidence
                  found in the candidate's resume.
                </p>
              </div>
            </div>

            <div
              className="input-card"
              onMouseMove={handleCardMove}
              onMouseLeave={handleCardLeave}
            >
              <label>JOB DESCRIPTION</label>

              <textarea
                className="large-input"
                value={jobDescription}
                onChange={(e) =>
                  setJobDescription(e.target.value)
                }
                placeholder="Paste the complete job description here..."
              />

              <div className="action-row">
                <span>
                  Resume context will be retrieved automatically.
                </span>

                <button
                  className="primary-button"
                  onClick={analyzeJob}
                  disabled={
                    loading ||
                    !jobDescription.trim()
                  }
                >
                  {loading
                    ? "Analyzing..."
                    : "Analyze Match →"}
                </button>
              </div>
            </div>

            {analysis && (
              <div
                className="result-card"
                onMouseMove={handleCardMove}
                onMouseLeave={handleCardLeave}
              >
                <div className="result-heading">
                  <span className="result-label">
                    JOB ANALYSIS
                  </span>

                  <span className="check">
                    ✓ COMPLETE
                  </span>
                </div>

                <div className="formatted-result">
                  {analysis}
                </div>
              </div>
            )}
          </section>
        )}

        {/* =============================
            INTERVIEW PREP
        ============================= */}

        {activeTab === "interview" && (
          <section className="workspace">
            <div
              className="hero-card"
              onMouseMove={handleCardMove}
              onMouseLeave={handleCardLeave}
            >
              <div className="hero-number">03</div>

              <div>
                <h2>Interview Preparation</h2>

                <p>
                  Generate questions based on the candidate's
                  resume and target job.
                </p>
              </div>
            </div>

            <div
              className="input-card"
              onMouseMove={handleCardMove}
              onMouseLeave={handleCardLeave}
            >
              <label>TARGET JOB DESCRIPTION</label>

              <textarea
                className="large-input"
                value={jobDescription}
                onChange={(e) =>
                  setJobDescription(e.target.value)
                }
                placeholder="Paste the job description you are preparing for..."
              />

              <div className="action-row">
                <span>
                  10 personalized questions will be generated.
                </span>

                <button
                  className="primary-button"
                  onClick={generateInterview}
                  disabled={
                    loading ||
                    !jobDescription.trim()
                  }
                >
                  {loading
                    ? "Generating..."
                    : "Generate Questions →"}
                </button>
              </div>
            </div>

            {interviewQuestions && (
              <div
                className="result-card"
                onMouseMove={handleCardMove}
                onMouseLeave={handleCardLeave}
              >
                <div className="result-heading">
                  <span className="result-label">
                    INTERVIEW QUESTIONS
                  </span>

                  <span className="check">
                    ✓ PERSONALIZED
                  </span>
                </div>

                <div className="formatted-result">
                  {interviewQuestions}
                </div>
              </div>
            )}
          </section>
        )}

        {/* =============================
            ERROR
        ============================= */}

        {error && (
          <div className="error-card">
            <strong>Something went wrong</strong>

            <p>{error}</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;