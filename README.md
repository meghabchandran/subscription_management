# Brightloop Subscription Management System

A subscription business management app: customers, products and variants, plans, quotations, subscriptions, taxes, invoices with recurring billing, payments, discounts and dashboards.

## Tech stack

| Layer    | Technology                                 |
| -------- | ------------------------------------------ |
| Backend  | Python, FastAPI, SQLAlchemy, Pydantic      |
| Database | SQLite (development)                       |
| Frontend | React, Vite, Tailwind CSS, React Router    |
| Auth     | JWT (python-jose), bcrypt password hashing |

## Architecture

```
Frontend (React)
   ↓
FastAPI routes
   ↓
Services / business logic
   ↓
SQLAlchemy models
   ↓
SQLite database
```

```
backend/
├── models/      # SQLAlchemy models
├── schemas/     # Pydantic request/response schemas
├── services/    # Business logic
├── routes/      # API endpoints
├── database.py  # DB configuration
├── main.py      # FastAPI app
└── seed.py      # Sample data
frontend/src/
├── pages/       # One folder per module
├── components/  # Shared components (e.g. CrudPage)
├── services/    # api.js (fetch helper)
├── App.jsx      # Routes and navigation
└── main.jsx
```

## Getting started

**Backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python seed.py                 # optional: load sample data (once)
uvicorn main:app --reload
```

API: http://127.0.0.1:8000 · Interactive docs: http://127.0.0.1:8000/docs

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

> The backend must allow the frontend origin through CORS (`CORSMiddleware` in `main.py`).
> If the database schema changes, delete `backend/brightloop.db` and restart so tables are recreated.

## Modules

| Module              | Covers                                    |
| ------------------- | ----------------------------------------- |
| Authentication      | Register, login                           |
| Customers           | Customer records                          |
| Products            | Products and product variants             |
| Plans               | Subscription plans and pricing            |
| Quotations          | Quotes with line items, 18% tax           |
| Subscriptions       | Lifecycle management                      |
| Taxes               | Tax rates                                 |
| Invoices            | Generation, line items, recurring billing |
| Payments            | Record and void payments against invoices |
| Discounts           | Evaluate, apply, usage tracking           |
| Dashboard / Reports | Revenue and KPIs                          |

## API overview

Full interactive reference at `/docs`.

| Area                               | Endpoints                                                                                                                           |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Auth `/auth`                       | `POST /register`, `POST /login`                                                                                                     |
| Products `/products`               | `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`                                                                         |
| Variants `/variants`               | `GET /`, `POST /`, `PUT /{id}`, `DELETE /{id}`                                                                                      |
| Plans `/plans`                     | `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`                                                                         |
| Quotations `/quotations`           | `GET /`, `POST /`, `GET /{id}`, `PUT /{id}/status`                                                                                  |
| Subscriptions `/subscriptions`     | `POST /`, `GET /`, `GET /{id}`, `POST /{id}/confirm`, `/activate`, `/pause`, `/renew`, `/close`                                     |
| Taxes `/taxes`                     | `POST /`, `GET /`, `GET /{id}`, `PUT /{id}`, `PATCH /{id}/deactivate`                                                               |
| Invoices `/invoices`               | `POST /`, `GET /`, `GET /{id}`, `GET /{id}/details`, `PATCH /{id}/status`, `POST /generate/{subscription_id}`, `POST /generate-due` |
| Payments `/payments`               | `POST`, `GET`, `GET /invoices`, `POST /{id}/void`                                                                                   |
| Discounts `/discounts`             | `GET`, `POST`, `PUT /{id}`, `DELETE /{id}`, `POST /evaluate`, `POST /apply`, `GET /{id}/usage`                                      |
| Dashboard `/dashboard`, `/reports` | `GET /revenue`, `GET /kpis`                                                                                                         |

## Key business flows

**Subscription lifecycle:** `draft → confirmed → active → paused → active → renew → closed`

**Pricing:** item total = `quantity × unit price − discount + tax`; invoice total = `subtotal − total discount + total tax`.

**Invoices:** sequential numbers (`INV-000001`), one invoice per subscription and billing period (duplicates rejected), line items copied from subscription items.

**Recurring billing:** `POST /invoices/generate-due` invoices every **active** subscription whose `next_billing_date` is today or earlier, then advances the date. It is triggered manually (no background scheduler).

## Frontend routes

| Route                        | Page                                    |
| ---------------------------- | --------------------------------------- |
| `/products`, `/variants`     | Product and variant management          |
| `/plans`                     | Subscription plans                      |
| `/quotations`                | Create and list quotations              |
| `/subscriptions`             | Subscription list and lifecycle actions |
| `/invoices`, `/invoices/:id` | Invoice list and details                |

## Demo flow

1. Add products, variants and plans (or load sample data)
2. Create a quotation for a customer
3. Create a subscription, then Confirm and Activate it
4. On `/invoices`, click **Generate due invoices**
5. Open the invoice to see items, tax and totals
6. Record a payment and watch the balance due drop

## Git workflow

Work on a feature branch, commit, pull the latest `dev`, merge, test, then open a Pull Request into `dev`. Do not push unfinished work to `main`.
