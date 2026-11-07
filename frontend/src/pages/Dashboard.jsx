import { useNavigate } from "react-router-dom";
import { clearToken } from "../api";

export default function Dashboard() {
  const navigate = useNavigate();

  function logout() {
    clearToken();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-slate-100 p-8">
      <div className="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-indigo-600">JobPilot</h1>
          <button
            onClick={logout}
            className="text-sm text-slate-600 hover:underline"
          >
            Log out
          </button>
        </div>
        <p className="mt-6 text-slate-600">
          You are logged in. Applications are coming next.
        </p>
      </div>
    </div>
  );
}
