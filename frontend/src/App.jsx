import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Products from "./pages/products/Products";
import Variants from "./pages/products/Variants";
import Plans from "./pages/plans/Plans";
import Quotations from "./pages/quotations/Quotations";
import Subscriptions from "./pages/subscriptions/Subscriptions";
import Invoices from "./pages/invoices/Invoices";
import InvoiceDetails from "./pages/invoices/InvoiceDetails";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-blue-700 p-4 text-white shadow">
          <h1 className="text-2xl font-bold">
            Brightloop Subscription Management
          </h1>

          <div className="mt-3 flex flex-wrap gap-4 text-sm">
            <a href="/products" className="hover:underline">
              Products
            </a>
            <a href="/variants" className="hover:underline">
              Variants
            </a>
            <a href="/plans" className="hover:underline">
              Plans
            </a>
            <a href="/quotations" className="hover:underline">
              Quotations
            </a>
            <a href="/subscriptions" className="hover:underline">
              Subscriptions
            </a>
            <a href="/invoices" className="hover:underline">
              Invoices
            </a>
          </div>
        </nav>

        <main className="p-6">
          <Routes>
            <Route path="/" element={<Navigate to="/products" replace />} />
            <Route path="/products" element={<Products />} />
            <Route path="/variants" element={<Variants />} />
            <Route path="/plans" element={<Plans />} />
            <Route path="/quotations" element={<Quotations />} />
            <Route path="/subscriptions" element={<Subscriptions />} />
            <Route path="/invoices" element={<Invoices />} />
            <Route path="/invoices/:id" element={<InvoiceDetails />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
