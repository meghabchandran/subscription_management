from datetime import date
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
    """Check whether an invoice already exists for this subscription
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

        # Generate a unique invoice number
    invoice_number = generate_invoice_number(db)

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

    # Get subscription items
    subscription_items = (
        db.query(SubscriptionItem)
        .filter(
            SubscriptionItem.subscription_id == subscription_id
        )
        .all()
    )

    # Calculate totals
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

    db.add(new_invoice)
    db.flush()

        # Create invoice items from subscription items
    for item in subscription_items:

        invoice_item = InvoiceItem(
            invoice_id=new_invoice.id,
            product_id=item.product_id,
            description=f"Subscription item for product ID {item.product_id}",
            quantity=item.quantity,
            unit_price=item.unit_price,
            discount_amount=item.discount_amount,
            tax_amount=item.tax_amount,
            total_amount=item.total_amount
        )

        db.add(invoice_item)

    # Save the invoice and all invoice items
    db.commit()
    db.refresh(new_invoice)

    return new_invoice