export const inr = (n) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(n || 0);

export const fmtDate = (d) => (d ? new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "-");

const tones = {
  green: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  amber: "bg-amber-50 text-amber-700 ring-amber-200",
  red: "bg-red-50 text-red-700 ring-red-200",
  gray: "bg-slate-100 text-slate-600 ring-slate-200",
  blue: "bg-sky-50 text-sky-700 ring-sky-200",
};

export const Badge = ({ tone = "gray", children }) => (
  <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${tones[tone]}`}>{children}</span>
);

export const PageHeader = ({ title, subtitle, action }) => (
  <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
    </div>
    {action}
  </div>
);

export const Kpi = ({ label, value, hint, tone }) => (
  <div className="rounded-lg border border-slate-200 bg-white p-4">
    <p className="text-sm text-slate-500">{label}</p>
    <p className={`mt-1 text-2xl font-semibold ${tone === "red" ? "text-red-600" : "text-slate-900"}`}>{value}</p>
    {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
  </div>
);

export const Table = ({ columns, rows, empty = "Nothing to show yet." }) => (
  <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
    <table className="min-w-full text-left text-sm">
      <thead className="bg-slate-50 text-slate-600">
        <tr>{columns.map((c) => <th key={c.header} className="whitespace-nowrap px-4 py-3 font-medium">{c.header}</th>)}</tr>
      </thead>
      <tbody className="divide-y divide-slate-100">
        {rows.length === 0 && <tr><td colSpan={columns.length} className="px-4 py-10 text-center text-slate-400">{empty}</td></tr>}
        {rows.map((r, i) => (
          <tr key={r.id ?? r.invoice_id ?? i} className="hover:bg-slate-50">
            {columns.map((c) => <td key={c.header} className="whitespace-nowrap px-4 py-3 text-slate-700">{c.render ? c.render(r) : r[c.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export const inputCls = "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500";
export const btnPrimary = "rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50";
export const btnGhost = "rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50";
