from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.quotation import Quotation
from models.quotation_item import QuotationItem
from schemas.quotation import (
    QuotationCreate,
    QuotationResponse,
    QuotationStatusUpdate
)
from services.quotation_service import create_quotation

router = APIRouter(prefix="/quotations", tags=["Quotations"])


@router.get("/", response_model=list[QuotationResponse])
def get_quotations(
    status: str | None = None,
    customer_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Quotation)

    if status:
        query = query.filter(Quotation.status == status)

    if customer_id is not None:
        query = query.filter(Quotation.customer_id == customer_id)

    return query.order_by(
        Quotation.id.desc()
    ).offset(skip).limit(limit).all()


@router.post("/", response_model=QuotationResponse, status_code=201)
def create_new_quotation(
    data: QuotationCreate,
    db: Session = Depends(get_db)
):
    return create_quotation(db, data)


@router.get("/{quotation_id}")
def get_quotation_details(
    quotation_id: int,
    db: Session = Depends(get_db)
):
    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id
    ).first()

    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    items = db.query(QuotationItem).filter(
        QuotationItem.quotation_id == quotation_id
    ).all()

    return {
        "quotation": QuotationResponse.model_validate(quotation),
        "items": items
    }


@router.put("/{quotation_id}/status")
def update_quotation_status(
    quotation_id: int,
    data: QuotationStatusUpdate,
    db: Session = Depends(get_db)
):
    quotation = db.query(Quotation).filter(
        Quotation.id == quotation_id
    ).first()

    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")

    quotation.status = data.status

    db.commit()
    db.refresh(quotation)

    return {
        "message": "Quotation status updated successfully",
        "quotation_id": quotation.id,
        "status": quotation.status
    }