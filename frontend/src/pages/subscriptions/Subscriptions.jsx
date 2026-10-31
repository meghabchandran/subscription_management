import { useEffect, useState } from "react";
import { apiRequest } from "../../services/api";

const STATUS_STYLE = {
  draft: "bg-gray-100 text-gray-700",
  confirmed: "bg-blue-100 text-blue-700",
  active: "bg-green-100 text-green-700",
  paused: "bg-amber-100 text-amber-700",
  closed: "bg-red-100 text-red-700",
};

// Which lifecycle buttons make sense for each status
const ACTIONS = {
  draft: ["confirm", "close"],
  confirmed: ["activate", "close"],
  active: ["pause", "renew", "close"],
  paused: ["activate", "renew", "close"],
  closed: [],
};

export default function Subscriptions() {
  const [subs, setSubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busyId, setBusyId] = useState(null);

  async function load() {
    try {
      setLoading(true);
      setError("");
      const data = await apiRequest("/subscriptions/");
      setSubs(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Error loading data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function runAction(sub, action) {
    let path = `/subscriptions/${sub.id}/${action}`;

    if (action === "renew") {
      const date = window.prompt(
        "New end date (YYYY-MM-DD):",
        sub.end_date || "",
      );
      if (!date) return;
      path += `?new_end_date=${encodeURIComponent(date)}`;
    }
    if (action === "close" && !window.confirm("Close this subscription?"))
      return;

    try {
      setBusyId(sub.id);
      setMessage("");
      await apiRequest(path, { method: "POST" });
      setMessage(`${sub.subscription_number}: ${action} successful`);
      await load();
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Subscriptions</h1>
          <p className="text-sm text-gray-500">
            Manage the subscription lifecycle.
          </p>
        </div>
        <button
          onClick={load}
          className="rounded-lg border bg-white px-3 py-2 text-sm hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>

      {message && (
        <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
          {message}
        </div>
      )}

      <div className="rounded-xl bg-white p-5 shadow-sm">
        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p className="text-red-600">Error loading data: {error}</p>
        ) : subs.length === 0 ? (
          <p className="text-gray-500">No data available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-3">Subscription #</th>
                  <th className="p-3">Customer</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Billing cycle</th>
                  <th className="p-3">Next billing</th>
                  <th className="p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {subs.map((s) => (
                  <tr key={s.id} className="border-b">
                    <td className="p-3 font-medium">{s.subscription_number}</td>
                    <td className="p-3">Customer #{s.customer_id}</td>
                    <td className="p-3">
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-medium capitalize ${STATUS_STYLE[s.status] || "bg-gray-100"}`}
                      >
                        {s.status}
                      </span>
                    </td>
                    <td className="p-3 capitalize">{s.billing_cycle}</td>
                    <td className="p-3">{s.next_billing_date || "-"}</td>
                    <td className="p-3">
                      <div className="flex flex-wrap gap-2">
                        {(ACTIONS[s.status] || []).map((a) => (
                          <button
                            key={a}
                            disabled={busyId === s.id}
                            onClick={() => runAction(s, a)}
                            className={`rounded px-3 py-1 text-xs capitalize disabled:opacity-50 ${
                              a === "close"
                                ? "bg-red-50 text-red-600 hover:bg-red-100"
                                : "bg-blue-50 text-blue-700 hover:bg-blue-100"
                            }`}
                          >
                            {a}
                          </button>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
