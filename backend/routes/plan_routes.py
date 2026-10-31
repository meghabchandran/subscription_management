from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.product import Product
from models.plan import Plan
from schemas.plan import PlanCreate, PlanUpdate, PlanResponse

router = APIRouter(prefix="/plans", tags=["Subscription Plans"])


@router.get("/", response_model=list[PlanResponse])
def get_plans(
    product_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Plan)

    if product_id is not None:
        query = query.filter(Plan.product_id == product_id)

    return query.offset(skip).limit(limit).all()


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return plan


@router.post("/", response_model=PlanResponse, status_code=201)
def create_plan(data: PlanCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == data.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")

    plan = Plan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    data: PlanUpdate,
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    updates = data.model_dump(exclude_unset=True)

    if "price" in updates and updates["price"] < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")

    for key, value in updates.items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)

    return plan


@router.delete("/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    db.delete(plan)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete plan because it is used in a quotation or subscription"
        )

    return {"message": "Plan deleted successfully"}