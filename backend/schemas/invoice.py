from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


# Base schema
class InvoiceBase(BaseModel):
    customer_id: int
    subscription_id: Optional[int] = None

    invoice_date: date
    due_date: date

    billing_period_start: date
    billing_period_end: date

    subtotal: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal

    amount_paid: Decimal = Decimal("0")
    balance_due: Decimal

    notes: Optional[str] = None


# Schema for creating an invoice
class InvoiceCreate(InvoiceBase):
    invoice_number: str


# Schema for updating an invoice
class InvoiceUpdate(BaseModel):
    due_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    amount_paid: Optional[Decimal] = None
    balance_due: Optional[Decimal] = None


# Schema for API responses
class InvoiceResponse(InvoiceBase):
    id: int
    invoice_number: str
    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)