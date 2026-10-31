import { useEffect, useState } from "react";
import { paymentsApi } from "../../services/api";
import { Badge, PageHeader, Table, inr, fmtDate, inputCls, btnPrimary, btnGhost } from "../../components/ui";

const METHODS = ["UPI", "Credit Card", "Debit Card", "Bank Transfer", "Cash"];
const TONE = { paid: "green", partial: "amber", unpaid: "gray", overdue: "red" };
const today = () => new Date().toISOString().slice(0, 10);
const blank = { invoice_id: "", payment_method: "UPI", amount: "", payment_date: today(), transaction_reference: "", notes: "" };

export default function Payments() {
  const [tab, setTab] = useState("invoices");       // invoices | history
  const [statusFilter, setStatusFilter] = useState("");
  const [invoices, setInvoices] = useState([]);
  const [history, setHistory] = useState([]);
  const [methodFilter, setMethodFilter] = useState("");
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");

  const loadInvoices = () => paymentsApi.invoices(statusFilter).then((r) => setInvoices(r.data));
  const loadHistory = () => paymentsApi.list({ method: methodFilter }).then((r) => setHistory(r.data));
  useEffect(() => { loadInvoices(); }, [statusFilter]);
  useEffect(() => { loadHistory(); }, [methodFilter]);

  const openForm = (inv) => {
    setError("");
    setForm({ ...blank, invoice_id: inv.id, amount: inv.balance_due, _inv: inv });
  };
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault(); setError("");
    const { _inv, ...body } = form;
    try {
      await paymentsApi.record({ ...body, invoice_id: Number(body.invoice_id), amount: Number(body.amount) });
      setForm(null); loadInvoices(); loadHistory();
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === "string" ? d : "Couldn't record the payment. Check the fields.");
    }
  };

  const voidPayment = async (p) => {
    if (!confirm(`Void ${p.payment_number}? The invoice balance will be restored.`)) return;
    await paymentsApi.void(p.id); loadInvoices(); loadHistory();
  };

  const invCols = [
    { header: "Invoice", key: "invoice_number" },
    { header: "Customer", key: "customer_name" },
    { header: "Due date", render: (r) => fmtDate(r.due_date) },
    { header: "Total", render: (r) => inr(r.total_amount) },
    { header: "Paid", render: (r) => inr(r.amount_paid) },
    { header: "Outstanding", render: (r) => inr(r.balance_due) },
    { header: "Status", render: (r) => <Badge tone={TONE[r.payment_status]}>{r.payment_status}</Badge> },
    { header: "", render: (r) => r.balance_due > 0 && <button className="text-indigo-600" onClick={() => openForm(r)}>Record payment</button> },
  ];
  const histCols = [
    { header: "Payment", key: "payment_number" },
    { header: "Invoice", key: "invoice_number" },
    { header: "Customer", key: "customer_name" },
    { header: "Date", render: (r) => fmtDate(r.payment_date) },
    { header: "Method", key: "payment_method" },
    { header: "Reference", render: (r) => r.transaction_reference || "-" },
    { header: "Amount", render: (r) => inr(r.amount) },
    { header: "Status", render: (r) => <Badge tone={r.payment_status === "Voided" ? "red" : "green"}>{r.payment_status}</Badge> },
    { header: "", render: (r) => r.payment_status === "Completed" && <button className="text-red-600" onClick={() => voidPayment(r)}>Void</button> },
  ];

  return (
    <div className="mx-auto max-w-7xl p-6">
      <PageHeader title="Payments" subtitle="Record payments against invoices and track what is still owed." />
      <div className="mb-4 flex flex-wrap items-center gap-2">
        {[["invoices", "Invoices"], ["history", "Payment history"]].map(([k, l]) => (
          <button key={k} onClick={() => setTab(k)}
            className={`rounded-md px-4 py-2 text-sm ${tab === k ? "bg-indigo-600 text-white" : "border border-slate-300 text-slate-700"}`}>{l}</button>
        ))}
        <div className="ml-auto">
          {tab === "invoices" ? (
            <select className={inputCls} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All invoices</option><option value="unpaid">Unpaid</option>
              <option value="partial">Partially paid</option><option value="overdue">Overdue</option><option value="paid">Paid</option>
            </select>
          ) : (
            <select className={inputCls} value={methodFilter} onChange={(e) => setMethodFilter(e.target.value)}>
              <option value="">All methods</option>{METHODS.map((m) => <option key={m}>{m}</option>)}
            </select>
          )}
        </div>
      </div>

      {tab === "invoices"
        ? <Table columns={invCols} rows={invoices} empty="No invoices match this filter." />
        : <Table columns={histCols} rows={history} empty="No payments recorded yet." />}

      {form && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-slate-900/40 p-4">
          <form onSubmit={save} className="w-full max-w-lg rounded-lg bg-white p-6">
            <h2 className="text-lg font-semibold">Record payment</h2>
            <p className="mb-4 text-sm text-slate-500">{form._inv.invoice_number} · {form._inv.customer_name} · {inr(form._inv.balance_due)} outstanding</p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <L label="Amount received (₹)"><input required type="number" step="0.01" min="0.01" max={form._inv.balance_due} className={inputCls} value={form.amount} onChange={set("amount")} /></L>
              <L label="Payment date"><input required type="date" className={inputCls} value={form.payment_date} onChange={set("payment_date")} /></L>
              <L label="Method">
                <select className={inputCls} value={form.payment_method} onChange={set("payment_method")}>{METHODS.map((m) => <option key={m}>{m}</option>)}</select>
              </L>
              <L label="Transaction reference"><input className={inputCls} value={form.transaction_reference} onChange={set("transaction_reference")} /></L>
              <div className="sm:col-span-2"><L label="Notes"><textarea rows="2" className={inputCls} value={form.notes} onChange={set("notes")} /></L></div>
            </div>
            {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" className={btnGhost} onClick={() => setForm(null)}>Cancel</button>
              <button className={btnPrimary}>Save payment</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

const L = ({ label, children }) => <label className="block text-sm text-slate-600">{label}<div className="mt-1">{children}</div></label>;
