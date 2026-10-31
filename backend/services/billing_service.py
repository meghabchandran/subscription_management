from datetime import date, timedelta
from decimal import Decimal


def calculate_tax_amount(
    amount: Decimal,
    tax_rate: Decimal
) -> Decimal:
    """Calculate the tax amount based on a percentage."""

    return (amount * tax_rate / Decimal("100")).quantize(
        Decimal("0.01")
    )


def calculate_total(
    subtotal: Decimal,
    discount_amount: Decimal,
    tax_amount: Decimal
) -> Decimal:
    """Calculate the final total amount."""

    return (
        subtotal
        - discount_amount
        + tax_amount
    ).quantize(Decimal("0.01"))


def calculate_item_total(
    quantity: int,
    unit_price: Decimal,
    discount_amount: Decimal,
    tax_amount: Decimal
) -> Decimal:
    """Calculate the total for a single item."""

    subtotal = Decimal(quantity) * unit_price

    return (
        subtotal
        - discount_amount
        + tax_amount
    ).quantize(Decimal("0.01"))


def calculate_next_billing_date(
    current_date: date,
    billing_cycle: str
) -> date:
    """Calculate the next billing date based on the billing cycle."""

    billing_cycle = billing_cycle.lower()

    if billing_cycle == "daily":
        return current_date + timedelta(days=1)

    elif billing_cycle == "weekly":
        return current_date + timedelta(weeks=1)

    elif billing_cycle == "monthly":
        # Simple monthly calculation for now
        return current_date + timedelta(days=30)

    elif billing_cycle == "yearly":
        return current_date + timedelta(days=365)

    else:
        raise ValueError(
            "Invalid billing cycle. "
            "Choose daily, weekly, monthly, or yearly."
        )