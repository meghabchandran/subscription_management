import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import { financeApi } from "../../services/api";
import FilterBar, { EMPTY_FILTERS } from "../../components/FilterBar";
import { Kpi, PageHeader, Table, inr, fmtDate, inputCls } from "../../components/ui";

const TABS = ["Revenue", "Subscriptions", "Payments", "Overdue invoices"];

export default function Reports() {
  const [tab, setTab] = useState(TABS[0]);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [search, setSearch] = useState("");
  const [data, setData] = useState(null);

  useEffect(() => {
    setData(null);
    const call = { Revenue: financeApi.revenue, Subscriptions: financeApi.subscriptions, Payments: financeApi.payments, "Overdue invoices": financeApi.overdue }[tab];
    call(filters).then((r) => setData(r.data));
  }, [tab, filters]);

  const exportCsv = (rows) => {
    if (!rows.length) return;
    const head = Object.keys(rows[0]);
    const csv = [head, ...rows.map((r) => head.map((h) => JSON.stringify(r[h] ?? "")))].map((r) => r.join(",")).join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = `${tab.toLowerCase().replace(" ", "-")}-report.csv`; a.click();
  };

  const overdueRows = (data || []).filter?.((r) => `${r.invoice_number} ${r.customer_name}`.toLowerCase().includes(search.toLowerCase())) || [];

  return (
    <div className="mx-auto max-w-7xl p-6">
      <PageHeader title="Reports" subtitle="Filter by date, customer, product, plan and status." />
      <div className="mb-4 flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`rounded-md px-4 py-2 text-sm ${tab === t ? "bg-indigo-600 text-white" : "border border-slate-300 text-slate-700"}`}>{t}</button>
        ))}
      </div>
      <FilterBar filters={filters} onChange={setFilters} />

      {!data && <p className="text-slate-400">Loading report…</p>}

      {data && tab === "Revenue" && (
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-medium">Monthly collected revenue</h2>
            <button className="text-sm text-indigo-600" onClick={() => exportCsv(data)}>Export CSV</button>
          </div>
          <div className="h-80">
            <ResponsiveContainer>
              <BarChart data={data}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="month" />
                <YAxis tickFormatter={(v) => `₹${v / 1000}K`} /><Tooltip formatter={(v) => inr(v)} />
                <Bar dataKey="revenue" fill="#4f46e5" radius={[4, 4, 0, 0]} /></BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {data && tab === "Subscriptions" && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          <Kpi label="Total subscriptions" value={data.total} />
          <Kpi label="Active" value={data.active} />
          <Kpi label="Expired" value={data.expired} />
          <Kpi label="Cancelled" value={data.cancelled} />
          <Kpi label="Renewals due (30 days)" value={data.renewals_due} />
        </div>
      )}

      {data && tab === "Payments" && (
        <>
          <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-3">
            <Kpi label="Total payments received" value={inr(data.total_received)} />
            <Kpi label="Pending payments" value={inr(data.pending)} hint="Not yet due" />
            <Kpi label="Outstanding balance" value={inr(data.outstanding)} hint="Pending plus overdue" />
          </div>
          <Table empty="No payments in this range." rows={data.by_method.map((m, i) => ({ ...m, id: i }))} columns={[
            { header: "Payment method", key: "method" }, { header: "Amount received", render: (r) => inr(r.amount) },
            { header: "Share", render: (r) => `${data.total_received ? Math.round((r.amount / data.total_received) * 100) : 0}%` },
          ]} />
        </>
      )}

      {data && tab === "Overdue invoices" && (
        <>
          <div className="mb-3 flex items-center justify-between gap-3">
            <input className={`${inputCls} max-w-sm`} placeholder="Search invoice or customer" value={search} onChange={(e) => setSearch(e.target.value)} />
            <button className="text-sm text-indigo-600" onClick={() => exportCsv(overdueRows)}>Export CSV</button>
          </div>
          <Table empty="No overdue invoices." rows={overdueRows} columns={[
            { header: "Invoice number", key: "invoice_number" }, { header: "Customer", key: "customer_name" },
            { header: "Invoice date", render: (r) => fmtDate(r.invoice_date) }, { header: "Due date", render: (r) => fmtDate(r.due_date) },
            { header: "Amount due", render: (r) => inr(r.amount_due) },
            { header: "Overdue days", render: (r) => <span className="font-medium text-red-600">{r.overdue_days}</span> },
          ]} />
        </>
      )}
    </div>
  );
}
