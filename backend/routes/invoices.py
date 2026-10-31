from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas.invoice import (
    InvoiceCreate,
    InvoiceResponse,
    InvoiceDetailsResponse
)
from datetime import date

from services.invoice_service import (
    create_invoice,
    get_invoices,
    get_invoice_by_id,
    get_invoice_details,
    generate_invoice_from_subscription,
    generate_due_invoices,
    update_invoice_status
)

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
)


# Database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()



@router.post(
    "/",
    response_model=InvoiceResponse
)
def create_new_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_invoice(db, invoice_data)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@router.get(
    "/",
    response_model=List[InvoiceResponse]
)
def read_invoices(
    db: Session = Depends(get_db)
):
    return get_invoices(db)

@router.post("/generate-due")
def generate_due_subscription_invoices(
    db: Session = Depends(get_db)
):
    invoices = generate_due_invoices(
        db,
        date.today()
    )

    return {
        "message": f"{len(invoices)} invoice(s) generated",
        "invoices": invoices
    }

@router.patch(
    "/{invoice_id}/status",
    response_model=InvoiceResponse
)
def update_existing_invoice_status(
    invoice_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    invoice = update_invoice_status(
        db,
        invoice_id,
        status
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    return invoice

@router.get(
    "/{invoice_id}/details",
    response_model=InvoiceDetailsResponse
)
def read_invoice_details(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    details = get_invoice_details(
        db,
        invoice_id
    )

    if not details:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    return details

@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse
)
def read_invoice(
    invoice_id: int,
    db: Session = Depends(get_db)
):
    invoice = get_invoice_by_id(
        db,
        invoice_id
    )

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    return invoice

@router.post(
    "/generate/{subscription_id}",
    response_model=InvoiceResponse
)
def generate_invoice(
    subscription_id: int,
    invoice_date: date,
    due_date: date,
    billing_period_start: date,
    billing_period_end: date,
    db: Session = Depends(get_db)
):
    try:
        invoice = generate_invoice_from_subscription(
            db=db,
            subscription_id=subscription_id,
            invoice_date=invoice_date,
            due_date=due_date,
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end
        )

        if not invoice:
            raise HTTPException(
                status_code=404,
                detail="Subscription not found"
            )

        return invoice

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )