import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";
import { financeApi } from "../../services/api";
import FilterBar, { EMPTY_FILTERS } from "../../components/FilterBar";
import { Kpi, PageHeader, Table, inr, fmtDate } from "../../components/ui";

const COLORS = ["#4f46e5", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444"];

export default function FinanceDashboard() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [kpis, setKpis] = useState(null);
  const [revenue, setRevenue] = useState([]);
  const [pay, setPay] = useState({ by_method: [] });
  const [overdue, setOverdue] = useState([]);

  useEffect(() => {
    Promise.all([financeApi.kpis(filters), financeApi.revenue(filters), financeApi.payments(filters), financeApi.overdue(filters)])
      .then(([k, r, p, o]) => { setKpis(k.data); setRevenue(r.data); setPay(p.data); setOverdue(o.data); });
  }, [filters]);

  return (
    <div className="mx-auto max-w-7xl p-6">
      <PageHeader title="Finance dashboard" subtitle="Revenue, collections and overdue invoices at a glance." />
      <FilterBar filters={filters} onChange={setFilters} />

      {kpis && (
        <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Kpi label="Revenue collected" value={inr(kpis.total_collected)} />
          <Kpi label="Outstanding balance" value={inr(kpis.outstanding)} hint={`${kpis.total_invoices - kpis.paid_invoices} unpaid invoices`} />
          <Kpi label="Overdue amount" tone="red" value={inr(kpis.overdue_amount)} hint={`${kpis.overdue_count} invoices`} />
          <Kpi label="Active subscriptions" value={kpis.active_subscriptions} hint={`of ${kpis.total_subscriptions} total`} />
        </div>
      )}

      <div className="mb-6 grid gap-4 lg:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-4 lg:col-span-2">
          <h2 className="mb-3 font-medium">Monthly collected revenue</h2>
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={revenue}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" /><YAxis tickFormatter={(v) => `₹${v / 1000}K`} />
                <Tooltip formatter={(v) => inr(v)} />
                <Bar dataKey="revenue" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="mb-3 font-medium">Payments by method</h2>
          <div className="h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={pay.by_method} dataKey="amount" nameKey="method" innerRadius={50} outerRadius={90}>
                  {pay.by_method.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => inr(v)} /><Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <h2 className="mb-3 font-medium">Overdue invoices</h2>
      <Table empty="No overdue invoices." rows={overdue.slice(0, 8)} columns={[
        { header: "Invoice", key: "invoice_number" }, { header: "Customer", key: "customer_name" },
        { header: "Due date", render: (r) => fmtDate(r.due_date) },
        { header: "Amount due", render: (r) => inr(r.amount_due) },
        { header: "Days overdue", render: (r) => <span className="font-medium text-red-600">{r.overdue_days}</span> },
      ]} />
    </div>
  );
}
