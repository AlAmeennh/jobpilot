import { useEffect, useState } from "react";
import { getStats } from "../api";

const CARDS = [
  { key: "Applied", color: "text-slate-700" },
  { key: "Interview", color: "text-amber-600" },
  { key: "Offer", color: "text-green-600" },
  { key: "Rejected", color: "text-red-600" },
];

export default function StatsBar({ version }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => setStats(null));
  }, [version]);

  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
      <div className="bg-white p-4 rounded-xl shadow text-center">
        <p className="text-2xl font-bold text-indigo-600">{stats.total}</p>
        <p className="text-sm text-slate-500">Total</p>
      </div>
      {CARDS.map((c) => (
        <div key={c.key} className="bg-white p-4 rounded-xl shadow text-center">
          <p className={`text-2xl font-bold ${c.color}`}>
            {stats.by_status[c.key]}
          </p>
          <p className="text-sm text-slate-500">{c.key}</p>
        </div>
      ))}
    </div>
  );
}
