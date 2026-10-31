import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../../services/api";
import { INVOICE_STATUS_STYLE, money } from "./invoiceUtils";

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  async function load() {
    try {
      setLoading(true);
      setError("");
      const data = await apiRequest("/invoices/");
      setInvoices(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Error loading data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function generateDue() {
    try {
      setMessage("");
      const res = await apiRequest("/invoices/generate-due", {
        method: "POST",
      });
      setMessage(res.message || "Done");
      await load();
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    }
  }

  const statuses = [...new Set(invoices.map((i) => i.status))];
  const visible = invoices.filter(
    (i) =>
      (!statusFilter || i.status === statusFilter) &&
      (!search ||
        i.invoice_number.toLowerCase().includes(search.toLowerCase())),
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Invoices</h1>
          <p className="text-sm text-gray-500">All generated invoices.</p>
        </div>
        <button
          onClick={generateDue}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Generate due invoices
        </button>
      </div>

      {message && (
        <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
          {message}
        </div>
      )}

      <div className="rounded-xl bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-wrap gap-3">
          <input
            placeholder="Search invoice number..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All statuses</option>
            {statuses.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : error ? (
          <p className="text-red-600">Error loading data: {error}</p>
        ) : visible.length === 0 ? (
          <p className="text-gray-500">No data available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-3">Invoice #</th>
                  <th className="p-3">Customer</th>
                  <th className="p-3">Invoice date</th>
                  <th className="p-3">Due date</th>
                  <th className="p-3">Total</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((inv) => (
                  <tr key={inv.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 font-medium">
                      <Link
                        to={`/invoices/${inv.id}`}
                        className="text-blue-600 hover:underline"
                      >
                        {inv.invoice_number}
                      </Link>
                    </td>
                    <td className="p-3">Customer #{inv.customer_id}</td>
                    <td className="p-3">{inv.invoice_date}</td>
                    <td className="p-3">{inv.due_date}</td>
                    <td className="p-3">{money(inv.total_amount)}</td>
                    <td className="p-3">
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-medium capitalize ${INVOICE_STATUS_STYLE[inv.status] || "bg-gray-100"}`}
                      >
                        {inv.status}
                      </span>
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
