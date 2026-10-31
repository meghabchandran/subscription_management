from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text
from datetime import datetime

from database import Base


class Tax(Base):
    __tablename__ = "taxes"

    id = Column(Integer, primary_key=True, index=True)

    # Tax details
    tax_name = Column(String(100), nullable=False)
    tax_type = Column(String(50), nullable=False)

    # Example: 18.00 for 18%
    tax_rate = Column(Numeric(5, 2), nullable=False)

    description = Column(Text, nullable=True)

    # Whether this tax is currently active
    is_active = Column(Boolean, default=True)

    # Record timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )