from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
from models import Discount, DiscountUsage

router = APIRouter(prefix="/discounts", tags=["Discounts"])


class DiscountIn(BaseModel):
    discount_name: str
    discount_code: Optional[str] = None
    description: Optional[str] = None
    discount_type: str = Field(pattern="^(Fixed|Percentage)$")
    discount_value: float = Field(gt=0)
    minimum_purchase: float = 0
    minimum_quantity: int = 0
    maximum_discount: Optional[float] = None
    start_date: date
    end_date: date
    usage_limit: Optional[int] = Field(default=None, gt=0)
    applicable_product_id: Optional[int] = None
    scope: str = Field(default="Product", pattern="^(Product|Subscription)$")
    status: str = "Active"


class DiscountOut(DiscountIn):
    id: int
    usage_count: int
    model_config = {"from_attributes": True}


class LineIn(BaseModel):
    product_id: int
    quantity: int
    amount: float          # line total before discount


class EvaluateIn(BaseModel):
    lines: List[LineIn]
    on_date: Optional[date] = None


class ApplyIn(EvaluateIn):
    customer_id: int
    invoice_id: Optional[int] = None
    subscription_id: Optional[int] = None


def _validate(d: DiscountIn):
    if d.end_date < d.start_date:
        raise HTTPException(400, "End date must be on or after start date")
    if d.discount_type == "Percentage" and d.discount_value > 100:
        raise HTTPException(400, "Percentage cannot exceed 100")
    if d.scope == "Product" and not d.applicable_product_id:
        raise HTTPException(400, "Select a product for product-scope discounts")


def best_discount(db: Session, lines, on_date=None):
    """Return (discount, amount) for the best eligible rule, or (None, 0).
    Rules stop applying when expired, usage limit reached, or minimums not met."""
    today = on_date or date.today()
    subtotal = sum(l.amount for l in lines)
    best, best_amt = None, 0.0
    rules = db.query(Discount).filter(
        Discount.status == "Active",
        Discount.start_date <= today, Discount.end_date >= today).all()
    for r in rules:
        if r.usage_limit is not None and r.usage_count >= r.usage_limit:
            continue
        if r.scope == "Product":
            pl = [l for l in lines if l.product_id == r.applicable_product_id]
            qty, base = sum(l.quantity for l in pl), sum(l.amount for l in pl)
        else:
            qty, base = sum(l.quantity for l in lines), subtotal
        if base <= 0 or subtotal < float(r.minimum_purchase or 0) or qty < (r.minimum_quantity or 0):
            continue
        val = float(r.discount_value)
        amt = val if r.discount_type == "Fixed" else base * val / 100
        if r.maximum_discount:
            amt = min(amt, float(r.maximum_discount))
        amt = round(min(amt, base), 2)
        if amt > best_amt:
            best, best_amt = r, amt
    return best, best_amt


@router.post("/evaluate")
def evaluate(data: EvaluateIn, db: Session = Depends(get_db)):
    d, amt = best_discount(db, data.lines, data.on_date)
    return {"discount_id": d.id if d else None, "discount_name": d.discount_name if d else None,
            "discount_amount": amt}


@router.post("/apply")
def apply(data: ApplyIn, db: Session = Depends(get_db)):
    """Member 3 calls this when generating an invoice: records usage and bumps usage_count."""
    d, amt = best_discount(db, data.lines, data.on_date)
    if not d:
        return {"discount_id": None, "discount_amount": 0}
    d.usage_count += 1
    db.add(DiscountUsage(discount_id=d.id, customer_id=data.customer_id, invoice_id=data.invoice_id,
                         subscription_id=data.subscription_id, discount_amount=amt))
    db.commit()
    return {"discount_id": d.id, "discount_name": d.discount_name, "discount_amount": amt}


@router.get("", response_model=List[DiscountOut])
def list_discounts(db: Session = Depends(get_db)):
    return db.query(Discount).order_by(Discount.id.desc()).all()


@router.post("", response_model=DiscountOut, status_code=201)
def create(data: DiscountIn, db: Session = Depends(get_db)):
    _validate(data)
    d = Discount(**data.model_dump())
    db.add(d); db.commit(); db.refresh(d)
    return d


@router.put("/{discount_id}", response_model=DiscountOut)
def update(discount_id: int, data: DiscountIn, db: Session = Depends(get_db)):
    _validate(data)
    d = db.get(Discount, discount_id)
    if not d:
        raise HTTPException(404, "Discount not found")
    for k, v in data.model_dump().items():
        setattr(d, k, v)
    db.commit(); db.refresh(d)
    return d


@router.delete("/{discount_id}")
def delete(discount_id: int, db: Session = Depends(get_db)):
    d = db.get(Discount, discount_id)
    if not d:
        raise HTTPException(404, "Discount not found")
    if d.usage_count > 0:           # keep history intact
        d.status = "Inactive"; db.commit()
        return {"message": "Discount already used, so it was deactivated instead of deleted"}
    db.delete(d); db.commit()
    return {"message": "Discount deleted"}


@router.get("/{discount_id}/usage")
def usage(discount_id: int, db: Session = Depends(get_db)):
    rows = db.query(DiscountUsage).filter_by(discount_id=discount_id).order_by(DiscountUsage.id.desc()).all()
    return [{"id": u.id, "customer_id": u.customer_id, "invoice_id": u.invoice_id,
             "discount_amount": float(u.discount_amount), "applied_at": u.applied_at} for u in rows]