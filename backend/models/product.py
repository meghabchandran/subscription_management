from sqlalchemy import Column, Integer, String, Text, Numeric
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(150), nullable=False)
    product_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(30), default="Active")