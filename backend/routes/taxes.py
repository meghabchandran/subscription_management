from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas.tax import TaxCreate, TaxUpdate, TaxResponse
from services.tax_service import (
    create_tax,
    get_taxes,
    get_tax_by_id,
    update_tax,
    deactivate_tax
)


router = APIRouter(
    prefix="/taxes",
    tags=["Taxes"]
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
    response_model=TaxResponse
)
def create_new_tax(
    tax_data: TaxCreate,
    db: Session = Depends(get_db)
):
    return create_tax(db, tax_data)


@router.get(
    "/",
    response_model=List[TaxResponse]
)
def read_taxes(
    db: Session = Depends(get_db)
):
    return get_taxes(db)


@router.get(
    "/{tax_id}",
    response_model=TaxResponse
)
def read_tax(
    tax_id: int,
    db: Session = Depends(get_db)
):
    tax = get_tax_by_id(db, tax_id)

    if not tax:
        raise HTTPException(
            status_code=404,
            detail="Tax not found"
        )

    return tax


@router.put(
    "/{tax_id}",
    response_model=TaxResponse
)
def update_existing_tax(
    tax_id: int,
    tax_data: TaxUpdate,
    db: Session = Depends(get_db)
):
    tax = update_tax(
        db,
        tax_id,
        tax_data
    )

    if not tax:
        raise HTTPException(
            status_code=404,
            detail="Tax not found"
        )

    return tax


@router.patch(
    "/{tax_id}/deactivate",
    response_model=TaxResponse
)
def deactivate_existing_tax(
    tax_id: int,
    db: Session = Depends(get_db)
):
    tax = deactivate_tax(db, tax_id)

    if not tax:
        raise HTTPException(
            status_code=404,
            detail="Tax not found"
        )

    return tax