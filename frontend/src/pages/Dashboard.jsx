import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import StatsBar from "../components/StatsBar";
import {
  clearToken,
  listApplications,
  createApplication,
  updateApplication,
  deleteApplication,
} from "../api";

const STATUSES = ["Applied", "Interview", "Offer", "Rejected"];

const BADGE = {
  Applied: "bg-slate-100 text-slate-700",
  Interview: "bg-amber-100 text-amber-800",
  Offer: "bg-green-100 text-green-800",
  Rejected: "bg-red-100 text-red-800",
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [apps, setApps] = useState([]);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [version, setVersion] = useState(0);

  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [jobUrl, setJobUrl] = useState("");

  async function load(statusFilter = filter) {
    try {
      setApps(await listApplications(statusFilter));
      setVersion((v) => v + 1);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAdd(e) {
    e.preventDefault();
    try {
      await createApplication({
        company: company.trim(),
        role: role.trim(),
        job_url: jobUrl.trim() || null,
      });
      setCompany("");
      setRole("");
      setJobUrl("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleStatus(id, status) {
    try {
      await updateApplication(id, { status });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this application?")) return;
    try {
      await deleteApplication(id);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  function changeFilter(value) {
    setFilter(value);
    load(value);
  }

  function logout() {
    clearToken();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-slate-100 p-4 sm:p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-indigo-600">JobPilot</h1>
          <div className="flex items-center gap-4">
            <Link
              to="/matcher"
              className="text-sm text-indigo-600 hover:underline"
            >
              Resume matcher
            </Link>
            <button
              onClick={logout}
              className="text-sm text-slate-600 hover:underline"
            >
              Log out
            </button>
          </div>
        </div>

        <StatsBar version={version} />
        <form
          onSubmit={handleAdd}
          className="bg-white p-6 rounded-xl shadow space-y-3"
        >
          <h2 className="font-semibold text-slate-800">Add an application</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              placeholder="Company"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              required
              className="border border-slate-300 rounded-lg px-3 py-2"
            />
            <input
              placeholder="Role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              required
              className="border border-slate-300 rounded-lg px-3 py-2"
            />
          </div>
          <input
            placeholder="Job link (optional)"
            value={jobUrl}
            onChange={(e) => setJobUrl(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2"
          />
          <button className="bg-indigo-600 text-white rounded-lg px-4 py-2 font-medium hover:bg-indigo-700">
            Add
          </button>
        </form>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div className="bg-white p-6 rounded-xl shadow">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-800">Your applications</h2>
            <select
              value={filter}
              onChange={(e) => changeFilter(e.target.value)}
              className="border border-slate-300 rounded-lg px-2 py-1 text-sm"
            >
              <option value="">All statuses</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {loading ? (
            <p className="text-slate-500">Loading...</p>
          ) : apps.length === 0 ? (
            <p className="text-slate-500">
              Nothing here yet. Add your first application above.
            </p>
          ) : (
            <ul className="divide-y divide-slate-200">
              {apps.map((a) => (
                <li
                  key={a.id}
                  className="py-3 flex flex-wrap items-center gap-3"
                >
                  <div className="flex-1 min-w-[10rem]">
                    <p className="font-medium text-slate-900">{a.role}</p>
                    <p className="text-sm text-slate-500">
                      {a.company}
                      {a.applied_on ? ` · ${a.applied_on}` : ""}
                    </p>
                    {a.job_url && (
                      <a
                        href={a.job_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm text-indigo-600 hover:underline"
                      >
                        View posting
                      </a>
                    )}
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${BADGE[a.status]}`}
                  >
                    {a.status}
                  </span>
                  <select
                    value={a.status}
                    onChange={(e) => handleStatus(a.id, e.target.value)}
                    className="border border-slate-300 rounded-lg px-2 py-1 text-sm"
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => handleDelete(a.id)}
                    className="text-sm text-red-600 hover:underline"
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
