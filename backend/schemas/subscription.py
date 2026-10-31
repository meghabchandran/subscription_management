from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# Base schema
class SubscriptionBase(BaseModel):
    customer_id: int
    quotation_id: Optional[int] = None

    start_date: date
    end_date: Optional[date] = None
    billing_start_date: date
    next_billing_date: Optional[date] = None

    billing_cycle: str
    auto_renew: bool = False


# Schema for creating a subscription
class SubscriptionCreate(SubscriptionBase):
    subscription_number: str


# Schema for updating a subscription
class SubscriptionUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    billing_start_date: Optional[date] = None
    next_billing_date: Optional[date] = None

    billing_cycle: Optional[str] = None
    status: Optional[str] = None
    auto_renew: Optional[bool] = None

    paused_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


# Schema for API responses
class SubscriptionResponse(SubscriptionBase):
    id: int
    subscription_number: str
    status: str

    paused_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)