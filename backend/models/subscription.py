from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    subscription_number = Column(
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

    quotation_id = Column(
        Integer,
        ForeignKey("quotations.id"),
        nullable=True
    )

    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    billing_start_date = Column(Date, nullable=False)
    next_billing_date = Column(Date, nullable=True)

    # Subscription details
    billing_cycle = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False, default="draft")
    auto_renew = Column(Boolean, default=False)

    # Status timestamps
    paused_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Record timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")
    quotation = relationship("Quotation", back_populates="subscriptions")

    items = relationship(
        "SubscriptionItem",
        back_populates="subscription"
    )