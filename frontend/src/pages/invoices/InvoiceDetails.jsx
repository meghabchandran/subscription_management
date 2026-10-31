import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiRequest } from "../../services/api";
import { INVOICE_STATUS_STYLE, money } from "./invoiceUtils";

const STATUS_OPTIONS = [
  "draft",
  "issued",
  "partial",
  "paid",
  "overdue",
  "cancelled",
];

export default function InvoiceDetails() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    try {
      setLoading(true);
      setError("");
      setData(await apiRequest(`/invoices/${id}/details`));
    } catch (err) {
      setError(err.message || "Error loading data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [id]);

  async function changeStatus(e) {
    try {
      setMessage("");
      await apiRequest(`/invoices/${id}/status?status=${e.target.value}`, {
        method: "PATCH",
      });
      setMessage("Status updated");
      await load();
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    }
  }

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-red-600">Error loading data: {error}</p>;
  if (!data || !data.invoice)
    return <p className="text-gray-500">No data available.</p>;

  const { invoice: inv, items = [] } = data;

  return (
    <div className="space-y-6">
      <Link to="/invoices" className="text-sm text-blue-600 hover:underline">
        ← Back to invoices
      </Link>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-gray-800">
          Invoice {inv.invoice_number}
        </h1>
        <div className="flex items-center gap-3">
          <span
            className={`rounded-full px-3 py-1 text-sm font-medium capitalize ${INVOICE_STATUS_STYLE[inv.status] || "bg-gray-100"}`}
          >
            {inv.status}
          </span>
          <select
            value={inv.status}
            onChange={changeStatus}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm"
          >
            {[...new Set([inv.status, ...STATUS_OPTIONS])].map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {message && (
        <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
          {message}
        </div>
      )}

      <div className="grid gap-4 rounded-xl bg-white p-5 text-sm shadow-sm sm:grid-cols-2 lg:grid-cols-4">
        <Info label="Customer" value={`Customer #${inv.customer_id}`} />
        <Info
          label="Subscription"
          value={inv.subscription_id ? `#${inv.subscription_id}` : "-"}
        />
        <Info label="Invoice date" value={inv.invoice_date} />
        <Info label="Due date" value={inv.due_date} />
        <Info
          label="Billing period"
          value={`${inv.billing_period_start} → ${inv.billing_period_end}`}
        />
      </div>

      <div className="rounded-xl bg-white p-5 shadow-sm">
        <h2 className="mb-3 text-lg font-semibold">Items</h2>
        {items.length === 0 ? (
          <p className="text-gray-500">No data available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-3">Product</th>
                  <th className="p-3">Qty</th>
                  <th className="p-3">Unit price</th>
                  <th className="p-3">Discount</th>
                  <th className="p-3">Tax</th>
                  <th className="p-3">Total</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it) => (
                  <tr key={it.id} className="border-b">
                    <td className="p-3">
                      {it.description || `Product #${it.product_id}`}
                    </td>
                    <td className="p-3">{it.quantity}</td>
                    <td className="p-3">{money(it.unit_price)}</td>
                    <td className="p-3">{money(it.discount_amount)}</td>
                    <td className="p-3">{money(it.tax_amount)}</td>
                    <td className="p-3 font-medium">
                      {money(it.total_amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="ml-auto max-w-sm space-y-2 rounded-xl bg-white p-5 text-sm shadow-sm">
        <Row label="Subtotal" value={money(inv.subtotal)} />
        <Row label="Discount" value={`- ${money(inv.discount_amount)}`} />
        <Row label="Tax" value={money(inv.tax_amount)} />
        <Row label="Total" value={money(inv.total_amount)} bold />
        <Row label="Amount paid" value={money(inv.amount_paid)} />
        <Row label="Balance due" value={money(inv.balance_due)} bold />
      </div>
    </div>
  );
}

const Info = ({ label, value }) => (
  <div>
    <p className="text-gray-500">{label}</p>
    <p className="font-medium">{value}</p>
  </div>
);

const Row = ({ label, value, bold }) => (
  <div
    className={`flex justify-between ${bold ? "border-t pt-2 font-semibold" : ""}`}
  >
    <span>{label}</span>
    <span>{value}</span>
  </div>
);
