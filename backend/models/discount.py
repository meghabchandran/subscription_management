from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, func
from database import Base


class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    discount_name = Column(String(150), nullable=False)
    discount_code = Column(String(50), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    discount_type = Column(String(20), nullable=False)            # Fixed | Percentage
    discount_value = Column(Numeric(12, 2), nullable=False)
    minimum_purchase = Column(Numeric(12, 2), default=0)
    minimum_quantity = Column(Integer, default=0)
    maximum_discount = Column(Numeric(12, 2), nullable=True)      # cap for percentage discounts
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    usage_limit = Column(Integer, nullable=True)                  # None = unlimited
    usage_count = Column(Integer, default=0, nullable=False)
    applicable_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    scope = Column(String(20), default="Product")                 # Product | Subscription
    status = Column(String(20), default="Active")                 # Active | Inactive
    created_at = Column(DateTime, server_default=func.now())