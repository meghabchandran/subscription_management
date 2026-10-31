from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional


class VariantCreate(BaseModel):
    product_id: int
    variant_name: str
    variant_code: str
    description: Optional[str] = None
    additional_price: Decimal = Decimal("0")
    status: str = "Active"


class VariantUpdate(BaseModel):
    variant_name: Optional[str] = None
    variant_code: Optional[str] = None
    description: Optional[str] = None
    additional_price: Optional[Decimal] = None
    status: Optional[str] = None


class VariantResponse(VariantCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)