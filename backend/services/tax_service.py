from sqlalchemy.orm import Session

from models.tax import Tax
from schemas.tax import TaxCreate, TaxUpdate


def create_tax(db: Session, tax_data: TaxCreate):
    """Create and save a new tax."""

    new_tax = Tax(
        tax_name=tax_data.tax_name,
        tax_type=tax_data.tax_type,
        tax_rate=tax_data.tax_rate,
        description=tax_data.description,
        is_active=tax_data.is_active
    )

    db.add(new_tax)
    db.commit()
    db.refresh(new_tax)

    return new_tax


def get_taxes(db: Session):
    """Get all taxes."""

    return db.query(Tax).all()


def get_tax_by_id(db: Session, tax_id: int):
    """Get one tax by its ID."""

    return (
        db.query(Tax)
        .filter(Tax.id == tax_id)
        .first()
    )


def update_tax(
    db: Session,
    tax_id: int,
    tax_data: TaxUpdate
):
    """Update an existing tax."""

    tax = get_tax_by_id(db, tax_id)

    if not tax:
        return None

    update_data = tax_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(tax, field, value)

    db.commit()
    db.refresh(tax)

    return tax


def deactivate_tax(db: Session, tax_id: int):
    """Deactivate a tax without deleting it."""

    tax = get_tax_by_id(db, tax_id)

    if not tax:
        return None

    tax.is_active = False

    db.commit()
    db.refresh(tax)

    return tax


def get_active_taxes(db: Session):
    """Get all currently active taxes."""

    return (
        db.query(Tax)
        .filter(Tax.is_active == True)
        .all()
    )