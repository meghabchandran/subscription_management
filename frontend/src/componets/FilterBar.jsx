import { useEffect, useState } from "react";
import { lookups } from "../services/api";
import { inputCls, btnGhost } from "./ui";

export const EMPTY_FILTERS = {
  date_from: "", date_to: "", customer_id: "", product_id: "", plan_id: "",
  subscription_status: "", invoice_status: "", payment_method: "",
};

const Field = ({ label, children }) => (
  <label className="block text-xs text-slate-500">{label}<div className="mt-1">{children}</div></label>
);

export default function FilterBar({ filters, onChange }) {
  const [opts, setOpts] = useState({ customers: [], products: [], plans: [] });

  useEffect(() => {
    Promise.allSettled([lookups.customers(), lookups.products(), lookups.plans()]).then(([c, p, pl]) =>
      setOpts({ customers: c.value?.data || [], products: p.value?.data || [], plans: pl.value?.data || [] })
    );
  }, []);

  const set = (k) => (e) => onChange({ ...filters, [k]: e.target.value });
  const select = (k, items, label) => (
    <select className={inputCls} value={filters[k]} onChange={set(k)}>
      <option value="">All</option>
      {items.map((i) => <option key={i.id} value={i.id}>{label(i)}</option>)}
    </select>
  );
  const fixed = (k, values) => (
    <select className={inputCls} value={filters[k]} onChange={set(k)}>
      <option value="">All</option>
      {values.map((v) => <option key={v}>{v}</option>)}
    </select>
  );

  return (
    <div className="mb-6 rounded-lg border border-slate-200 bg-white p-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Field label="From"><input type="date" className={inputCls} value={filters.date_from} onChange={set("date_from")} /></Field>
        <Field label="To"><input type="date" className={inputCls} value={filters.date_to} onChange={set("date_to")} /></Field>
        <Field label="Customer">{select("customer_id", opts.customers, (c) => c.company_name)}</Field>
        <Field label="Product">{select("product_id", opts.products, (p) => p.product_name)}</Field>
        <Field label="Plan">{select("plan_id", opts.plans, (p) => p.plan_name)}</Field>
        <Field label="Subscription status">{fixed("subscription_status", ["Active", "Expired", "Cancelled", "Paused"])}</Field>
        <Field label="Invoice status">{fixed("invoice_status", ["Confirmed", "Paid"])}</Field>
        <Field label="Payment method">{fixed("payment_method", ["UPI", "Credit Card", "Debit Card", "Bank Transfer", "Cash"])}</Field>
      </div>
      <div className="mt-3 text-right">
        <button className={btnGhost} onClick={() => onChange(EMPTY_FILTERS)}>Clear filters</button>
      </div>
    </div>
  );
}
