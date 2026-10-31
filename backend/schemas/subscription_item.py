from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


# Base schema
class SubscriptionItemBase(BaseModel):
    product_id: int
    plan_id: int
    variant_id: Optional[int] = None

    quantity: int = 1

    unit_price: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal


# Schema for creating a subscription item
class SubscriptionItemCreate(SubscriptionItemBase):
    subscription_id: int


# Schema for updating a subscription item
class SubscriptionItemUpdate(BaseModel):
    product_id: Optional[int] = None
    plan_id: Optional[int] = None
    variant_id: Optional[int] = None

    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None


# Schema for API responses
class SubscriptionItemResponse(SubscriptionItemBase):
    id: int
    subscription_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)