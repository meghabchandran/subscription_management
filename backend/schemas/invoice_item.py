from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


# Base schema
class InvoiceItemBase(BaseModel):
    product_id: int
    description: Optional[str] = None

    quantity: int = 1

    unit_price: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal


# Schema for creating an invoice item
class InvoiceItemCreate(InvoiceItemBase):
    invoice_id: int


# Schema for updating an invoice item
class InvoiceItemUpdate(BaseModel):
    product_id: Optional[int] = None
    description: Optional[str] = None

    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None


# Schema for API responses
class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int

    model_config = ConfigDict(from_attributes=True)