from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from database import Base


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    # Item details
    description = Column(String(500), nullable=True)

    quantity = Column(Integer, nullable=False, default=1)

    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    # Relationships
    invoice = relationship(
        "Invoice",
        back_populates="items"
    )

    product = relationship("Product")