from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from datetime import date
from typing import Optional, List, Literal


class QuotationItemCreate(BaseModel):
    product_id: int
    plan_id: Optional[int] = None
    variant_id: Optional[int] = None
    quantity: int = Field(default=1, ge=1)
    discount_amount: Decimal = Decimal("0")


class QuotationCreate(BaseModel):
    customer_id: int
    created_by: int
    valid_until: date
    discount_amount: Decimal = Decimal("0")
    notes: Optional[str] = None
    items: List[QuotationItemCreate]


class QuotationStatusUpdate(BaseModel):
    status: Literal["Draft", "Sent", "Accepted", "Rejected", "Expired"]


class QuotationItemResponse(QuotationItemCreate):
    id: int
    unit_price: Decimal
    tax_amount: Decimal
    total_amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class QuotationResponse(BaseModel):
    id: int
    quotation_number: str
    customer_id: int
    created_by: int
    quotation_date: date
    valid_until: date
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: str
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)