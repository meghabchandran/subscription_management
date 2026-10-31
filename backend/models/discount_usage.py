from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from database import Base


class DiscountUsage(Base):
    __tablename__ = "discount_usage"

    id = Column(Integer, primary_key=True, index=True)
    discount_id = Column(Integer, ForeignKey("discounts.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customers_id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    discount_amount = Column(Numeric(12, 2), nullable=False)
    applied_at = Column(DateTime, server_default=func.now())