from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.product import Product
from models.product_variant import ProductVariant
from schemas.product_variant import (
    VariantCreate,
    VariantUpdate,
    VariantResponse
)

router = APIRouter(prefix="/variants", tags=["Product Variants"])


@router.get("/", response_model=list[VariantResponse])
def get_variants(
    product_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ProductVariant)

    if product_id is not None:
        query = query.filter(ProductVariant.product_id == product_id)

    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=VariantResponse, status_code=201)
def create_variant(data: VariantCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == data.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    variant = ProductVariant(**data.model_dump())
    db.add(variant)

    try:
        db.commit()
        db.refresh(variant)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Variant code already exists")

    return variant


@router.put("/{variant_id}", response_model=VariantResponse)
def update_variant(
    variant_id: int,
    data: VariantUpdate,
    db: Session = Depends(get_db)
):
    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id
    ).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(variant, key, value)

    try:
        db.commit()
        db.refresh(variant)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Variant code already exists")

    return variant


@router.delete("/{variant_id}")
def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id
    ).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    db.delete(variant)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete variant because it is used in a quotation"
        )

    return {"message": "Variant deleted successfully"}