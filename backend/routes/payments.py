from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
from models import Payment, PaymentAllocation, Invoice, Customer

router = APIRouter(prefix="/payments", tags=["Payments"])
METHODS = {"UPI", "Credit Card", "Debit Card", "Bank Transfer", "Cash"}


class PaymentIn(BaseModel):
    invoice_id: int
    payment_method: str
    amount: float = Field(gt=0)
    payment_date: date
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None


def payment_status(inv: Invoice, today=None) -> str:
    """paid | partial | overdue | unpaid  (kept separate from Draft/Confirmed/Paid)"""
    today = today or date.today()
    bal = float(inv.balance_due or 0)
    if bal <= 0:
        return "paid"
    if inv.due_date and inv.due_date < today:
        return "overdue"
    return "partial" if float(inv.amount_paid or 0) > 0 else "unpaid"


def _row(p, inv, cust):
    return {"id": p.id, "payment_number": p.payment_number, "invoice_id": p.invoice_id,
            "invoice_number": inv.invoice_number, "customer_id": p.customer_id,
            "customer_name": cust.company_name, "payment_date": p.payment_date,
            "amount": float(p.amount), "payment_method": p.payment_method,
            "transaction_reference": p.transaction_reference,
            "payment_status": p.payment_status, "notes": p.notes}


@router.post("", status_code=201)
def record_payment(data: PaymentIn, db: Session = Depends(get_db)):
    if data.payment_method not in METHODS:
        raise HTTPException(400, f"Method must be one of {sorted(METHODS)}")
    inv = db.get(Invoice, data.invoice_id)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    if inv.status == "Draft":
        raise HTTPException(400, "Confirm the invoice before recording payment")
    balance = float(inv.balance_due)
    if data.amount > balance + 0.001:
        raise HTTPException(400, f"Amount exceeds balance due (₹{balance:,.2f})")

    count = db.query(Payment).count() + 1
    p = Payment(payment_number=f"PAY-{count:06d}", invoice_id=inv.id, customer_id=inv.customer_id,
                payment_date=data.payment_date, amount=data.amount, payment_method=data.payment_method,
                transaction_reference=data.transaction_reference, notes=data.notes)
    db.add(p); db.flush()
    db.add(PaymentAllocation(payment_id=p.id, invoice_id=inv.id, amount=data.amount))
    inv.amount_paid = float(inv.amount_paid or 0) + data.amount
    inv.balance_due = round(float(inv.total_amount) - float(inv.amount_paid), 2)
    if inv.balance_due <= 0:
        inv.status = "Paid"
    db.commit(); db.refresh(p)
    return {"id": p.id, "payment_number": p.payment_number, "invoice_status": inv.status,
            "balance_due": float(inv.balance_due)}


@router.get("")
def payment_history(invoice_id: Optional[int] = None, customer_id: Optional[int] = None,
                    method: Optional[str] = None, date_from: Optional[date] = None,
                    date_to: Optional[date] = None, db: Session = Depends(get_db)):
    q = db.query(Payment, Invoice, Customer).join(Invoice, Payment.invoice_id == Invoice.id) \
          .join(Customer, Payment.customer_id == Customer.id)
    if invoice_id: q = q.filter(Payment.invoice_id == invoice_id)
    if customer_id: q = q.filter(Payment.customer_id == customer_id)
    if method: q = q.filter(Payment.payment_method == method)
    if date_from: q = q.filter(Payment.payment_date >= date_from)
    if date_to: q = q.filter(Payment.payment_date <= date_to)
    return [_row(*r) for r in q.order_by(Payment.payment_date.desc(), Payment.id.desc()).all()]


@router.get("/invoices")
def invoice_payment_status(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Invoices with computed payment status. status = paid | unpaid | partial | overdue"""
    rows = db.query(Invoice, Customer).join(Customer, Invoice.customer_id == Customer.id) \
             .filter(Invoice.status != "Draft").order_by(Invoice.due_date).all()
    out = []
    for inv, c in rows:
        s = payment_status(inv)
        if status and s != status:
            continue
        out.append({"id": inv.id, "invoice_number": inv.invoice_number, "customer_name": c.company_name,
                    "invoice_date": inv.invoice_date, "due_date": inv.due_date,
                    "total_amount": float(inv.total_amount), "amount_paid": float(inv.amount_paid or 0),
                    "balance_due": float(inv.balance_due or 0), "payment_status": s})
    return out


@router.post("/{payment_id}/void")
def void_payment(payment_id: int, db: Session = Depends(get_db)):
    p = db.get(Payment, payment_id)
    if not p or p.payment_status == "Voided":
        raise HTTPException(404, "Payment not found or already voided")
    inv = db.get(Invoice, p.invoice_id)
    p.payment_status = "Voided"
    inv.amount_paid = max(0, float(inv.amount_paid) - float(p.amount))
    inv.balance_due = round(float(inv.total_amount) - float(inv.amount_paid), 2)
    if inv.status == "Paid" and inv.balance_due > 0:
        inv.status = "Confirmed"
    db.commit()
    return {"message": "Payment voided", "invoice_status": inv.status}