from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from models.invoice import Invoice
from models.invoice_item import InvoiceItem
from models.subscription import Subscription
from models.subscription_item import SubscriptionItem

from schemas.invoice import InvoiceCreate
from services.billing_service import calculate_total


def create_invoice(
    db: Session,
    invoice_data: InvoiceCreate
):
    """Create and save a new invoice."""

    # Prevent duplicate invoices for the same subscription
    # and billing period
    if invoice_data.subscription_id:
        existing_invoice = invoice_exists_for_period(
            db,
            invoice_data.subscription_id,
            invoice_data.billing_period_start,
            invoice_data.billing_period_end
        )

        if existing_invoice:
            raise ValueError(
                "An invoice already exists for this subscription "
                "and billing period."
            )


    new_invoice = Invoice(
        invoice_number=invoice_data.invoice_number,
        customer_id=invoice_data.customer_id,
        subscription_id=invoice_data.subscription_id,
        invoice_date=invoice_data.invoice_date,
        due_date=invoice_data.due_date,
        billing_period_start=invoice_data.billing_period_start,
        billing_period_end=invoice_data.billing_period_end,
        subtotal=invoice_data.subtotal,
        discount_amount=invoice_data.discount_amount,
        tax_amount=invoice_data.tax_amount,
        total_amount=invoice_data.total_amount,
        amount_paid=invoice_data.amount_paid,
        balance_due=invoice_data.balance_due,
        notes=invoice_data.notes
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice


def get_invoices(db: Session):
    """Get all invoices."""

    return db.query(Invoice).all()


def get_invoice_by_id(
    db: Session,
    invoice_id: int
):
    """Get one invoice by its ID."""

    return (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )


def invoice_exists_for_period(
    db: Session,
    subscription_id: int,
    billing_period_start: date,
    billing_period_end: date
):
    """Check whether an invoice already exists for a subscription
    and billing period.
    """

    return (
        db.query(Invoice)
        .filter(
            Invoice.subscription_id == subscription_id,
            Invoice.billing_period_start == billing_period_start,
            Invoice.billing_period_end == billing_period_end
        )
        .first()
    )


def generate_invoice_number(db: Session):
    """Generate a unique invoice number."""

    last_invoice = (
        db.query(Invoice)
        .order_by(Invoice.id.desc())
        .first()
    )

    if not last_invoice:
        return "INV-000001"

    next_number = last_invoice.id + 1

    return f"INV-{next_number:06d}"


def get_next_billing_date(
    current_date: date,
    billing_cycle: str
):
    """Calculate the next billing date based on the billing cycle."""

    billing_cycle = billing_cycle.lower()

    if billing_cycle == "monthly":
        return current_date + timedelta(days=30)

    elif billing_cycle == "quarterly":
        return current_date + timedelta(days=90)

    elif billing_cycle == "yearly":
        return current_date + timedelta(days=365)

    return current_date


def generate_invoice_from_subscription(
    db: Session,
    subscription_id: int,
    invoice_date: date,
    due_date: date,
    billing_period_start: date,
    billing_period_end: date
):
    """Generate an invoice and invoice items from a subscription."""

    # Get the subscription
    subscription = (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id)
        .first()
    )

    if not subscription:
        return None

    # Prevent duplicate invoices
    existing_invoice = invoice_exists_for_period(
        db,
        subscription_id,
        billing_period_start,
        billing_period_end
    )

    if existing_invoice:
        raise ValueError(
            "An invoice already exists for this subscription "
            "and billing period."
        )

    # Generate a unique invoice number
    invoice_number = generate_invoice_number(db)

    # Get subscription items
    subscription_items = (
        db.query(SubscriptionItem)
        .filter(
            SubscriptionItem.subscription_id == subscription_id
        )
        .all()
    )

    # Calculate invoice totals
    subtotal = Decimal("0")
    total_discount = Decimal("0")
    total_tax = Decimal("0")

    for item in subscription_items:
        item_subtotal = (
            Decimal(item.quantity) * item.unit_price
        )

        subtotal += item_subtotal
        total_discount += item.discount_amount
        total_tax += item.tax_amount

    total_amount = calculate_total(
        subtotal,
        total_discount,
        total_tax
    )

    # Create the invoice
    new_invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=subscription.customer_id,
        subscription_id=subscription.id,
        invoice_date=invoice_date,
        due_date=due_date,
        billing_period_start=billing_period_start,
        billing_period_end=billing_period_end,
        subtotal=subtotal,
        discount_amount=total_discount,
        tax_amount=total_tax,
        total_amount=total_amount,
        amount_paid=Decimal("0"),
        balance_due=total_amount,
        status="issued"
    )

    # Add invoice to the database
    db.add(new_invoice)

    # Flush to generate the invoice ID before creating invoice items
    db.flush()

    # Create invoice items from subscription items
    for item in subscription_items:

        item_subtotal = (
            Decimal(item.quantity) * item.unit_price
        )

        item_total = (
            item_subtotal
            - item.discount_amount
            + item.tax_amount
        )

        invoice_item = InvoiceItem(
            invoice_id=new_invoice.id,
            product_id=item.product_id,
            description=(
                f"Subscription item for product ID "
                f"{item.product_id}"
            ),
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount_amount=item.discount_amount,
            tax_amount=item.tax_amount,
            total_amount=item_total
        )

        db.add(invoice_item)

    # Update the subscription's next billing date
    subscription.next_billing_date = get_next_billing_date(
        billing_period_end,
        subscription.billing_cycle
    )

    # Save the invoice, invoice items, and subscription update
    db.commit()
    db.refresh(new_invoice)

    return new_invoice

def get_due_subscriptions(
    db: Session,
    current_date: date
):
    """Get active subscriptions that are due for billing."""

    return (
        db.query(Subscription)
        .filter(
            Subscription.status == "active",
            Subscription.next_billing_date <= current_date
        )
        .all()
    )

def generate_due_invoices(
    db: Session,
    current_date: date
):
    """Generate invoices for all subscriptions due for billing."""

    due_subscriptions = get_due_subscriptions(
        db,
        current_date
    )

    generated_invoices = []

    for subscription in due_subscriptions:

        billing_period_start = subscription.next_billing_date

        # For now, use a simple 30-day billing period
        billing_period_end = (
            billing_period_start
            + timedelta(days=30)
        )

        invoice = generate_invoice_from_subscription(
            db=db,
            subscription_id=subscription.id,
            invoice_date=current_date,
            due_date=current_date + timedelta(days=7),
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end
        )

        generated_invoices.append(invoice)

    return generated_invoices