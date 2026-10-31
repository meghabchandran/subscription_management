from sqlalchemy import (
    Column, Integer, String, Date, Numeric,
    ForeignKey, Text
)
from datetime import date
from database import Base
from sqlalchemy.orm import relationship


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)

    quotation_number = Column(String(50), unique=True, nullable=False)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    subscriptions = relationship(
    "Subscription",
    back_populates="quotation"
   )

    quotation_date = Column(Date, default=date.today)
    valid_until = Column(Date, nullable=False)

    subtotal = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)

    status = Column(String(30), default="Draft")
    notes = Column(Text, nullable=True)