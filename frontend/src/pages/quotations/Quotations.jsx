
import { useEffect, useState } from "react";
import { apiRequest } from "../../services/api";

export default function Quotations() {
  const [quotations, setQuotations] = useState([]);
  const [products, setProducts] = useState([]);
  const [plans, setPlans] = useState([]);
  const [variants, setVariants] = useState([]);
  const [message, setMessage] = useState("");

  const [form, setForm] = useState({
    quotation_number: "",
    customer_id: "",
    created_by: "",
    valid_until: "",
    notes: "",
    product_id: "",
    plan_id: "",
    variant_id: "",
    quantity: 1,
    discount_amount: 0,
  });

  async function loadData() {
    try {
      const [q, p, pl, v] = await Promise.all([
        apiRequest("/quotations/"),
        apiRequest("/products/"),
        apiRequest("/plans/"),
        apiRequest("/variants/"),
      ]);

      setQuotations(Array.isArray(q) ? q : []);
      setProducts(Array.isArray(p) ? p : []);
      setPlans(Array.isArray(pl) ? pl : []);
      setVariants(Array.isArray(v) ? v : []);
    } catch (error) {
      setMessage(error.message);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function change(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function createQuotation(e) {
    e.preventDefault();
    setMessage("");

    const payload = {
      quotation_number: form.quotation_number,
      customer_id: Number(form.customer_id),
      created_by: Number(form.created_by),
      valid_until: form.valid_until,
      notes: form.notes || null,
      items: [
        {
          product_id: Number(form.product_id),
          plan_id: form.plan_id ? Number(form.plan_id) : null,
          variant_id: form.variant_id ? Number(form.variant_id) : null,
          quantity: Number(form.quantity),
          discount_amount: Number(form.discount_amount || 0),
        },
      ],
    };

    try {
      await apiRequest("/quotations/", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setMessage("Quotation created successfully!");

      setForm({
        quotation_number: "",
        customer_id: "",
        created_by: "",
        valid_until: "",
        notes: "",
        product_id: "",
        plan_id: "",
        variant_id: "",
        quantity: 1,
        discount_amount: 0,
      });

      loadData();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">
          Quotation Management
        </h1>
        <p className="text-sm text-gray-500">
          Create and manage customer quotations.
        </p>
      </div>

      {message && (
        <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
          {message}
        </div>
      )}

      <form
        onSubmit={createQuotation}
        className="grid gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2"
      >
        <h2 className="text-lg font-semibold md:col-span-2">
          Create Quotation
        </h2>

        <div>
          <label className="mb-1 block text-sm">Quotation Number</label>
          <input
            name="quotation_number"
            value={form.quotation_number}
            onChange={change}
            required
            className="w-full rounded-lg border p-2"
            placeholder="QUO-001"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm">Customer ID</label>
          <input
            name="customer_id"
            type="number"
            value={form.customer_id}
            onChange={change}
            required
            min="1"
            className="w-full rounded-lg border p-2"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm">Created By (User ID)</label>
          <input
            name="created_by"
            type="number"
            value={form.created_by}
            onChange={change}
            required
            min="1"
            className="w-full rounded-lg border p-2"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm">Valid Until</label>
          <input
            name="valid_until"
            type="date"
            value={form.valid_until}
            onChange={change}
            required
            className="w-full rounded-lg border p-2"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm">Product</label>
          <select
            name="product_id"
            value={form.product_id}
            onChange={change}
            required
            className="w-full rounded-lg border p-2"
          >
            <option value="">Select product</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.product_name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm">Subscription Plan</label>
          <select
            name="plan_id"
            value={form.plan_id}
            onChange={change}
            className="w-full rounded-lg border p-2"
          >
            <option value="">No plan selected</option>
            {plans
              .filter(
                (p) =>
                  !form.product_id ||
                  String(p.product_id) === String(form.product_id)
              )
              .map((p) => (
                <option key={p.id} value={p.id}>
                  {p.plan_name} - {p.price}
                </option>
              ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm">Product Variant</label>
          <select
            name="variant_id"
            value={form.variant_id}
            onChange={change}
            className="w-full rounded-lg border p-2"
          >
            <option value="">No variant selected</option>
            {variants
              .filter(
                (v) =>
                  !form.product_id ||
                  String(v.product_id) === String(form.product_id)
              )
              .map((v) => (
                <option key={v.id} value={v.id}>
                  {v.variant_name}
                </option>
              ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm">Quantity</label>
          <input
            name="quantity"
            type="number"
            min="1"
            value={form.quantity}
            onChange={change}
            required
            className="w-full rounded-lg border p-2"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm">Discount Amount</label>
          <input
            name="discount_amount"
            type="number"
            min="0"
            value={form.discount_amount}
            onChange={change}
            className="w-full rounded-lg border p-2"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm">Notes</label>
          <input
            name="notes"
            value={form.notes}
            onChange={change}
            className="w-full rounded-lg border p-2"
          />
        </div>

        <button
          type="submit"
          className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 md:col-span-2"
        >
          Create Quotation
        </button>
      </form>

      <div className="rounded-xl bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold">Quotation List</h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-3">Quotation No.</th>
                <th className="p-3">Customer ID</th>
                <th className="p-3">Date</th>
                <th className="p-3">Total</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>

            <tbody>
              {quotations.map((q) => (
                <tr key={q.id} className="border-b">
                  <td className="p-3">{q.quotation_number}</td>
                  <td className="p-3">{q.customer_id}</td>
                  <td className="p-3">{q.quotation_date}</td>
                  <td className="p-3">{q.total_amount}</td>
                  <td className="p-3">{q.status}</td>
                </tr>
              ))}

              {quotations.length === 0 && (
                <tr>
                  <td colSpan="5" className="p-4 text-center text-gray-500">
                    No quotations available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
