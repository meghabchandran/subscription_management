from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional


class PlanCreate(BaseModel):
    product_id: int
    plan_name: str
    description: Optional[str] = None
    billing_cycle: str
    billing_interval: int = 1
    price: Decimal
    minimum_quantity: int = 1
    maximum_quantity: Optional[int] = None
    trial_days: int = 0
    auto_renew: bool = True
    status: str = "Active"


class PlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    description: Optional[str] = None
    billing_cycle: Optional[str] = None
    billing_interval: Optional[int] = None
    price: Optional[Decimal] = None
    minimum_quantity: Optional[int] = None
    maximum_quantity: Optional[int] = None
    trial_days: Optional[int] = None
    auto_renew: Optional[bool] = None
    status: Optional[str] = None


class PlanResponse(PlanCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)