from sqlalchemy import (
    Column, Integer, Numeric, ForeignKey
)
from database import Base


class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id = Column(Integer, primary_key=True, index=True)

    quotation_id = Column(
        Integer,
        ForeignKey("quotations.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    plan_id = Column(
        Integer,
        ForeignKey("plans.id"),
        nullable=True
    )

    variant_id = Column(
        Integer,
        ForeignKey("product_variants.id"),
        nullable=True
    )

    quantity = Column(Integer, nullable=False, default=1)

    unit_price = Column(Numeric(10, 2), nullable=False)

    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)