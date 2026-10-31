from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Customer(Base):
    __tablename__ = "customers"

    customers_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    subscriptions = relationship(
        "Subscription",
        back_populates="customer"
    )