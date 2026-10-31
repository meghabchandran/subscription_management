from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional


class ProductCreate(BaseModel):
    product_name: str
    product_code: str
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Decimal
    status: str = "Active"


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[Decimal] = None
    status: Optional[str] = None


class ProductResponse(ProductCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)