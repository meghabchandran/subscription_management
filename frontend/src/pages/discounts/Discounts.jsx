import { useEffect, useMemo, useState } from "react";
import { discountsApi, lookups } from "../../services/api";
import { Badge, PageHeader, Table, inr, fmtDate, inputCls, btnPrimary, btnGhost } from "../../components/ui";

const blank = {
  discount_name: "", discount_code: "", description: "", discount_type: "Percentage", discount_value: "",
  minimum_purchase: 0, minimum_quantity: 0, maximum_discount: "", start_date: "", end_date: "",
  usage_limit: "", applicable_product_id: "", scope: "Product", status: "Active",
};

// Expired / exhausted rules stop applying automatically, so show the real state
export function effectiveStatus(d) {
  const today = new Date().toISOString().slice(0, 10);
  if (d.status !== "Active") return ["Inactive", "gray"];
  if (d.end_date < today) return ["Expired", "red"];
  if (d.start_date > today) return ["Scheduled", "blue"];
  if (d.usage_limit && d.usage_count >= d.usage_limit) return ["Limit reached", "amber"];
  return ["Active", "green"];
}

export default function Discounts() {
  const [rows, setRows] = useState([]);
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(null);       // null = closed
  const [editId, setEditId] = useState(null);
  const [usage, setUsage] = useState(null);
  const [error, setError] = useState("");

  const load = () => discountsApi.list().then((r) => setRows(r.data));
  useEffect(() => { load(); lookups.products().then((r) => setProducts(r.data)).catch(() => {}); }, []);

  const productName = (id) => products.find((p) => p.id === id)?.product_name || "-";
  const shown = useMemo(
    () => rows.filter((d) => `${d.discount_name} ${d.discount_code || ""}`.toLowerCase().includes(search.toLowerCase())),
    [rows, search]
  );

  const open = (d) => {
    setError(""); setEditId(d?.id ?? null);
    setForm(d ? { ...blank, ...Object.fromEntries(Object.entries(d).map(([k, v]) => [k, v ?? ""])) } : blank);
  };
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault(); setError("");
    const num = (v) => (v === "" ? null : Number(v));
    const body = {
      ...form,
      discount_code: form.discount_code || null,
      discount_value: Number(form.discount_value),
      minimum_purchase: Number(form.minimum_purchase || 0),
      minimum_quantity: Number(form.minimum_quantity || 0),
      maximum_discount: num(form.maximum_discount),
      usage_limit: num(form.usage_limit),
      applicable_product_id: form.scope === "Product" ? num(form.applicable_product_id) : null,
    };
    try {
      editId ? await discountsApi.update(editId, body) : await discountsApi.create(body);
      setForm(null); load();
    } catch (err) {
      const d = err.response?.data?.detail;
      setError(typeof d === "string" ? d : "Check the form fields and try again.");
    }
  };

  const remove = async (d) => {
    if (!confirm(`Delete "${d.discount_name}"?`)) return;
    await discountsApi.remove(d.id); load();
  };

  const columns = [
    { header: "Name", render: (d) => <div><p className="font-medium">{d.discount_name}</p>{d.discount_code && <p className="text-xs text-slate-400">{d.discount_code}</p>}</div> },
    { header: "Discount", render: (d) => (d.discount_type === "Fixed" ? inr(d.discount_value) : `${d.discount_value}%`) },
    { header: "Conditions", render: (d) => `Min ${inr(d.minimum_purchase)} / ${d.minimum_quantity} units` },
    { header: "Applies to", render: (d) => (d.scope === "Product" ? productName(d.applicable_product_id) : "Whole subscription") },
    { header: "Validity", render: (d) => `${fmtDate(d.start_date)} to ${fmtDate(d.end_date)}` },
    { header: "Usage", render: (d) => `${d.usage_count}${d.usage_limit ? ` / ${d.usage_limit}` : ""}` },
    { header: "Status", render: (d) => { const [t, tone] = effectiveStatus(d); return <Badge tone={tone}>{t}</Badge>; } },
    { header: "", render: (d) => (
      <div className="flex gap-3 text-sm">
        <button className="text-indigo-600" onClick={() => discountsApi.usage(d.id).then((r) => setUsage({ d, rows: r.data }))}>Usage</button>
        <button className="text-indigo-600" onClick={() => open(d)}>Edit</button>
        <button className="text-red-600" onClick={() => remove(d)}>Delete</button>
      </div>) },
  ];

  return (
    <div className="mx-auto max-w-7xl p-6">
      <PageHeader title="Discounts" subtitle="Rules apply automatically to the next invoice when a customer qualifies."
        action={<button className={btnPrimary} onClick={() => open(null)}>Create discount</button>} />
      <input className={`${inputCls} mb-4 max-w-sm`} placeholder="Search by name or code" value={search} onChange={(e) => setSearch(e.target.value)} />
      <Table columns={columns} rows={shown} empty="No discounts yet. Create one to start." />

      {form && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-slate-900/40 p-4">
          <form onSubmit={save} className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold">{editId ? "Edit discount" : "Create discount"}</h2>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <L label="Discount name"><input required className={inputCls} value={form.discount_name} onChange={set("discount_name")} /></L>
              <L label="Code (optional)"><input className={inputCls} value={form.discount_code} onChange={set("discount_code")} /></L>
              <L label="Type">
                <select className={inputCls} value={form.discount_type} onChange={set("discount_type")}>
                  <option value="Percentage">Percentage</option><option value="Fixed">Fixed amount</option>
                </select>
              </L>
              <L label={form.discount_type === "Fixed" ? "Amount (₹)" : "Percentage (%)"}>
                <input required type="number" min="0.01" step="0.01" max={form.discount_type === "Percentage" ? 100 : undefined} className={inputCls} value={form.discount_value} onChange={set("discount_value")} />
              </L>
              <L label="Minimum purchase (₹)"><input type="number" min="0" className={inputCls} value={form.minimum_purchase} onChange={set("minimum_purchase")} /></L>
              <L label="Minimum quantity"><input type="number" min="0" className={inputCls} value={form.minimum_quantity} onChange={set("minimum_quantity")} /></L>
              <L label="Start date"><input required type="date" className={inputCls} value={form.start_date} onChange={set("start_date")} /></L>
              <L label="End date"><input required type="date" className={inputCls} value={form.end_date} onChange={set("end_date")} /></L>
              <L label="Usage limit (blank = unlimited)"><input type="number" min="1" className={inputCls} value={form.usage_limit} onChange={set("usage_limit")} /></L>
              {form.discount_type === "Percentage" && (
                <L label="Maximum discount (₹, optional)"><input type="number" min="0" className={inputCls} value={form.maximum_discount} onChange={set("maximum_discount")} /></L>
              )}
              <L label="Scope">
                <select className={inputCls} value={form.scope} onChange={set("scope")}>
                  <option>Product</option><option>Subscription</option>
                </select>
              </L>
              {form.scope === "Product" && (
                <L label="Applicable product">
                  <select required className={inputCls} value={form.applicable_product_id} onChange={set("applicable_product_id")}>
                    <option value="">Select product</option>
                    {products.map((p) => <option key={p.id} value={p.id}>{p.product_name}</option>)}
                  </select>
                </L>
              )}
              <L label="Status">
                <select className={inputCls} value={form.status} onChange={set("status")}>
                  <option value="Active">Active</option><option value="Inactive">Inactive</option>
                </select>
              </L>
            </div>
            {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" className={btnGhost} onClick={() => setForm(null)}>Cancel</button>
              <button className={btnPrimary}>Save discount</button>
            </div>
          </form>
        </div>
      )}

      {usage && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-slate-900/40 p-4">
          <div className="w-full max-w-xl rounded-lg bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold">Usage: {usage.d.discount_name}</h2>
            <Table empty="This discount hasn't been used yet." columns={[
              { header: "Customer ID", key: "customer_id" }, { header: "Invoice ID", key: "invoice_id" },
              { header: "Discount", render: (r) => inr(r.discount_amount) }, { header: "Applied", render: (r) => fmtDate(r.applied_at) },
            ]} rows={usage.rows} />
            <div className="mt-4 text-right"><button className={btnGhost} onClick={() => setUsage(null)}>Close</button></div>
          </div>
        </div>
      )}
    </div>
  );
}

const L = ({ label, children }) => <label className="block text-sm text-slate-600">{label}<div className="mt-1">{children}</div></label>;
