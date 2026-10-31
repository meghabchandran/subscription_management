from collections import defaultdict
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Payment, Invoice, InvoiceItem, Subscription, SubscriptionItem, Customer

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
reports_router = APIRouter(prefix="/reports", tags=["Reports"])   # include both in main.py


class Filters:
    def __init__(self, date_from: Optional[date] = None, date_to: Optional[date] = None,
                 customer_id: Optional[int] = None, product_id: Optional[int] = None,
                 plan_id: Optional[int] = None, subscription_status: Optional[str] = None,
                 invoice_status: Optional[str] = None, payment_method: Optional[str] = None):
        self.date_from, self.date_to = date_from, date_to
        self.customer_id, self.product_id, self.plan_id = customer_id, product_id, plan_id
        self.subscription_status = subscription_status
        self.invoice_status, self.payment_method = invoice_status, payment_method


def _sub_ids(db, f):
    q = db.query(Subscription.id)
    if f.plan_id or f.product_id:
        q = q.join(SubscriptionItem, SubscriptionItem.subscription_id == Subscription.id)
        if f.plan_id: q = q.filter(SubscriptionItem.plan_id == f.plan_id)
        if f.product_id: q = q.filter(SubscriptionItem.product_id == f.product_id)
    if f.subscription_status: q = q.filter(Subscription.status == f.subscription_status)
    return q


def invoices_q(db, f):
    q = db.query(Invoice, Customer).join(Customer, Invoice.customer_id == Customer.id).filter(Invoice.status != "Draft")
    if f.date_from: q = q.filter(Invoice.invoice_date >= f.date_from)
    if f.date_to: q = q.filter(Invoice.invoice_date <= f.date_to)
    if f.customer_id: q = q.filter(Invoice.customer_id == f.customer_id)
    if f.invoice_status: q = q.filter(Invoice.status == f.invoice_status)
    if f.product_id:
        q = q.filter(Invoice.id.in_(db.query(InvoiceItem.invoice_id).filter(InvoiceItem.product_id == f.product_id)))
    if f.plan_id or f.subscription_status:
        q = q.filter(Invoice.subscription_id.in_(_sub_ids(db, f)))
    return q


def payments_q(db, f):
    q = db.query(Payment, Invoice).join(Invoice, Payment.invoice_id == Invoice.id).filter(Payment.payment_status == "Completed")
    if f.date_from: q = q.filter(Payment.payment_date >= f.date_from)
    if f.date_to: q = q.filter(Payment.payment_date <= f.date_to)
    if f.customer_id: q = q.filter(Payment.customer_id == f.customer_id)
    if f.payment_method: q = q.filter(Payment.payment_method == f.payment_method)
    if f.invoice_status: q = q.filter(Invoice.status == f.invoice_status)
    if f.product_id:
        q = q.filter(Invoice.id.in_(db.query(InvoiceItem.invoice_id).filter(InvoiceItem.product_id == f.product_id)))
    if f.plan_id or f.subscription_status:
        q = q.filter(Invoice.subscription_id.in_(_sub_ids(db, f)))
    return q


def _overdue(db, f):
    today = date.today()
    out = []
    for inv, c in invoices_q(db, f).filter(Invoice.balance_due > 0, Invoice.due_date < today).order_by(Invoice.due_date):
        out.append({"invoice_id": inv.id, "invoice_number": inv.invoice_number, "customer_name": c.company_name,
                    "invoice_date": inv.invoice_date, "due_date": inv.due_date,
                    "amount_due": float(inv.balance_due), "overdue_days": (today - inv.due_date).days})
    return out


@router.get("/revenue")
def revenue(f: Filters = Depends(), db: Session = Depends(get_db)):
    """Monthly collected revenue."""
    m = defaultdict(float)
    for p, _ in payments_q(db, f).all():
        m[p.payment_date.strftime("%Y-%m")] += float(p.amount)
    return [{"month": k, "revenue": round(v, 2)} for k, v in sorted(m.items())]


@router.get("/kpis")
def kpis(f: Filters = Depends(), db: Session = Depends(get_db)):
    total = sum(float(p.amount) for p, _ in payments_q(db, f).all())
    invs = [i for i, _ in invoices_q(db, f).all()]
    today = date.today()
    outstanding = sum(float(i.balance_due or 0) for i in invs)
    overdue = sum(float(i.balance_due or 0) for i in invs if i.balance_due and i.balance_due > 0 and i.due_date < today)
    subs = _sub_ids(db, f).count() if (f.plan_id or f.product_id or f.subscription_status) else db.query(Subscription).count()
    active = db.query(Subscription).filter(Subscription.status == "Active").count()
    return {"total_collected": total, "outstanding": outstanding, "overdue_amount": overdue,
            "overdue_count": len(_overdue(db, f)), "total_invoices": len(invs),
            "paid_invoices": sum(1 for i in invs if float(i.balance_due or 0) <= 0),
            "total_subscriptions": subs, "active_subscriptions": active}


@reports_router.get("/subscriptions")
def subscription_report(f: Filters = Depends(), db: Session = Depends(get_db)):
    q = db.query(Subscription)
    if f.customer_id: q = q.filter(Subscription.customer_id == f.customer_id)
    if f.date_from: q = q.filter(Subscription.start_date >= f.date_from)
    if f.date_to: q = q.filter(Subscription.start_date <= f.date_to)
    if f.plan_id or f.product_id or f.subscription_status:
        q = q.filter(Subscription.id.in_(_sub_ids(db, f)))
    subs = q.all()
    soon = date.today() + timedelta(days=30)
    count = lambda s: sum(1 for x in subs if (x.status or "").lower() == s)
    return {"total": len(subs), "active": count("active"), "expired": count("expired"),
            "cancelled": count("cancelled"),
            "renewals_due": sum(1 for x in subs if (x.status or "").lower() == "active"
                                and x.next_billing_date and x.next_billing_date <= soon)}


@reports_router.get("/payments")
def payment_report(f: Filters = Depends(), db: Session = Depends(get_db)):
    by_method = defaultdict(float)
    total = 0.0
    for p, _ in payments_q(db, f).all():
        by_method[p.payment_method] += float(p.amount); total += float(p.amount)
    today = date.today()
    open_invs = [i for i, _ in invoices_q(db, f).filter(Invoice.balance_due > 0).all()]
    return {"total_received": total,
            "by_method": [{"method": k, "amount": round(v, 2)} for k, v in by_method.items()],
            "pending": sum(float(i.balance_due) for i in open_invs if i.due_date >= today),
            "outstanding": sum(float(i.balance_due) for i in open_invs)}


@reports_router.get("/overdue")
def overdue_report(f: Filters = Depends(), db: Session = Depends(get_db)):
    return _overdue(db, f)