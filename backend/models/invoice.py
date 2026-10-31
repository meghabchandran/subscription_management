from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Text
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # Foreign keys
    customer_id = Column(
        Integer,
        ForeignKey("customers.customers_id"),
        nullable=False
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=True
    )

    # Invoice dates
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    # Billing period
    billing_period_start = Column(Date, nullable=False)
    billing_period_end = Column(Date, nullable=False)

    # Amounts
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    amount_paid = Column(Numeric(10, 2), default=0)
    balance_due = Column(Numeric(10, 2), nullable=False)

    # Invoice status
    status = Column(String(30), nullable=False, default="draft")

    notes = Column(Text, nullable=True)

    # Record timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    customer = relationship("Customer")
    subscription = relationship("Subscription")

    items = relationship(
        "InvoiceItem",
        back_populates="invoice"
    )