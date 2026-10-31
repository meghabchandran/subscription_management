import axios from "axios";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000" });

api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem("token");
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

// drop empty filter values before sending
export const clean = (obj) => Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== "" && v != null));

export const discountsApi = {
  list: () => api.get("/discounts"),
  create: (d) => api.post("/discounts", d),
  update: (id, d) => api.put(`/discounts/${id}`, d),
  remove: (id) => api.delete(`/discounts/${id}`),
  usage: (id) => api.get(`/discounts/${id}/usage`),
};

export const paymentsApi = {
  list: (params) => api.get("/payments", { params: clean(params || {}) }),
  record: (d) => api.post("/payments", d),
  void: (id) => api.post(`/payments/${id}/void`),
  invoices: (status) => api.get("/payments/invoices", { params: clean({ status }) }),
};

export const financeApi = {
  kpis: (f) => api.get("/dashboard/kpis", { params: clean(f) }),
  revenue: (f) => api.get("/dashboard/revenue", { params: clean(f) }),
  subscriptions: (f) => api.get("/reports/subscriptions", { params: clean(f) }),
  payments: (f) => api.get("/reports/payments", { params: clean(f) }),
  overdue: (f) => api.get("/reports/overdue", { params: clean(f) }),
};

// lookups owned by other members
export const lookups = {
  customers: () => api.get("/customers"),
  products: () => api.get("/products"),
  plans: () => api.get("/plans"),
};

export default api;