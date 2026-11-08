import { useState } from "react";
import { Link } from "react-router-dom";
import { matchResume, matchResumePdf } from "../api";

const MAX_PDF_MB = 5;

function SkillList({ title, skills, color }) {
  return (
    <div>
      <h3 className="font-semibold text-slate-800 mb-2">{title}</h3>
      {skills.length === 0 ? (
        <p className="text-sm text-slate-500">None</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {skills.map((s) => (
            <span key={s} className={`text-sm px-2 py-1 rounded-full ${color}`}>
              {s}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function MatcherPage() {
  const [mode, setMode] = useState("pdf");
  const [jd, setJd] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleFile(e) {
    const picked = e.target.files[0];
    setError("");
    if (!picked) {
      setFile(null);
      return;
    }
    if (picked.size > MAX_PDF_MB * 1024 * 1024) {
      setError(`PDF is too large (max ${MAX_PDF_MB} MB)`);
      setFile(null);
      e.target.value = "";
      return;
    }
    setFile(picked);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);

    if (mode === "pdf" && !file) {
      setError("Please choose a PDF file");
      return;
    }

    setLoading(true);
    try {
      const data =
        mode === "pdf"
          ? await matchResumePdf(jd, file)
          : await matchResume(jd, resumeText);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const tabClass = (active) =>
    `px-3 py-1 rounded-lg text-sm font-medium ${
      active ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-700"
    }`;

  return (
    <div className="min-h-screen bg-slate-100 p-4 sm:p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-indigo-600">Resume Matcher</h1>
          <Link to="/" className="text-sm text-slate-600 hover:underline">
            Back to applications
          </Link>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white p-6 rounded-xl shadow space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Job description
            </label>
            <textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              required
              minLength={30}
              rows={6}
              placeholder="Paste the job description here (at least 30 characters)"
              className="w-full border border-slate-300 rounded-lg px-3 py-2"
            />
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium text-slate-700 mr-2">
                Your resume
              </span>
              <button
                type="button"
                onClick={() => setMode("pdf")}
                className={tabClass(mode === "pdf")}
              >
                Upload PDF
              </button>
              <button
                type="button"
                onClick={() => setMode("text")}
                className={tabClass(mode === "text")}
              >
                Paste text
              </button>
            </div>

            {mode === "pdf" ? (
              <div>
                <input
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFile}
                  className="block w-full text-sm text-slate-600 border border-slate-300 rounded-lg p-2"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Text-based PDF, up to {MAX_PDF_MB} MB. The text is sent to
                  Google's Gemini for analysis, and the file itself is not
                  stored.
                </p>
              </div>
            ) : (
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                required
                minLength={30}
                rows={6}
                placeholder="Paste your resume text here (at least 30 characters)"
                className="w-full border border-slate-300 rounded-lg px-3 py-2"
              />
            )}
          </div>

          <button
            disabled={loading}
            className="bg-indigo-600 text-white rounded-lg px-4 py-2 font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? "Analysing..." : "Analyse match"}
          </button>
          {error && <p className="text-red-600 text-sm">{error}</p>}
        </form>

        {result && (
          <div className="bg-white p-6 rounded-xl shadow space-y-5">
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold text-indigo-600">
                {result.match_score}%
              </div>
              <p className="text-slate-600">match with this job</p>
            </div>
            <SkillList
              title="Matched skills"
              skills={result.matched_skills}
              color="bg-green-100 text-green-800"
            />
            <SkillList
              title="Missing skills"
              skills={result.missing_skills}
              color="bg-red-100 text-red-800"
            />
            <div>
              <h3 className="font-semibold text-slate-800 mb-2">Suggestions</h3>
              <ul className="list-disc pl-5 space-y-1 text-slate-700">
                {result.suggestions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
