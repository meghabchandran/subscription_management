
import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";

export default function CrudPage({
  title,
  endpoint,
  fields,
  columns,
}) {
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState({});
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadRecords() {
    try {
      setLoading(true);
      const data = await apiRequest(endpoint);
      setRecords(Array.isArray(data) ? data : []);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRecords();
  }, [endpoint]);

  function handleChange(e) {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");

    const payload = {};

    fields.forEach((field) => {
      let value = form[field.name];

      if (value === undefined || value === "") {
        if (field.required) return;
        if (field.type === "number") {
          payload[field.name] = null;
        }
        return;
      }

      if (field.type === "number") {
        value = Number(value);
      }

      payload[field.name] = value;
    });

    payload.status = "Active";

    try {
      await apiRequest(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      });

      setMessage(`${title} added successfully!`);
      setForm({});
      await loadRecords();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Do you want to delete this record?")) return;

    try {
      await apiRequest(`${endpoint}${id}`, {
        method: "DELETE",
      });

      setMessage("Record deleted successfully!");
      await loadRecords();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">{title}</h1>
        <p className="text-sm text-gray-500">
          Manage your {title.toLowerCase()}.
        </p>
      </div>

      {message && (
        <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
          {message}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-xl bg-white p-5 shadow-sm"
        >
          <h2 className="text-lg font-semibold">Add {title}</h2>

          {fields.map((field) => (
            <div key={field.name}>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                {field.label}
              </label>

              <input
                type={field.type || "text"}
                name={field.name}
                value={form[field.name] || ""}
                onChange={handleChange}
                required={field.required}
                min={field.min}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 outline-none focus:border-blue-500"
              />
            </div>
          ))}

          <button
            type="submit"
            className="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700"
          >
            Add {title}
          </button>
        </form>

        <div className="rounded-xl bg-white p-5 shadow-sm lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">{title} List</h2>
            <button
              onClick={loadRecords}
              type="button"
              className="rounded-lg border px-3 py-2 text-sm hover:bg-gray-50"
            >
              Refresh
            </button>
          </div>

          {loading ? (
            <p>Loading...</p>
          ) : records.length === 0 ? (
            <p className="text-gray-500">No records available.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    {columns.map((column) => (
                      <th key={column.key} className="p-3">
                        {column.label}
                      </th>
                    ))}
                    <th className="p-3">Action</th>
                  </tr>
                </thead>

                <tbody>
                  {records.map((record) => (
                    <tr key={record.id} className="border-b">
                      {columns.map((column) => (
                        <td key={column.key} className="p-3">
                          {record[column.key] ?? "-"}
                        </td>
                      ))}

                      <td className="p-3">
                        <button
                          onClick={() => handleDelete(record.id)}
                          className="rounded bg-red-50 px-3 py-1 text-red-600 hover:bg-red-100"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
