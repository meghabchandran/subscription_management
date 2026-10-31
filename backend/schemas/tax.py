from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


# Base schema
class TaxBase(BaseModel):
    tax_name: str
    tax_type: str
    tax_rate: Decimal
    description: Optional[str] = None
    is_active: bool = True


# Schema for creating a tax
class TaxCreate(TaxBase):
    pass


# Schema for updating a tax
class TaxUpdate(BaseModel):
    tax_name: Optional[str] = None
    tax_type: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Schema for API responses
class TaxResponse(TaxBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)