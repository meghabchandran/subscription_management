from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey
from database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    plan_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    billing_cycle = Column(String(30), nullable=False)
    billing_interval = Column(Integer, default=1)

    price = Column(Numeric(10, 2), nullable=False)

    minimum_quantity = Column(Integer, default=1)
    maximum_quantity = Column(Integer, nullable=True)

    trial_days = Column(Integer, default=0)
    auto_renew = Column(Boolean, default=True)

    status = Column(String(30), default="Active")