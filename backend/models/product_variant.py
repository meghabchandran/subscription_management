from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    variant_name = Column(String(150), nullable=False)
    variant_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    additional_price = Column(Numeric(10, 2), default=0)
    status = Column(String(30), default="Active")