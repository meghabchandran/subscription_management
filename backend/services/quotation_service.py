from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.product import Product
from models.product_variant import ProductVariant
from models.plan import Plan
from models.quotation import Quotation
from models.quotation_item import QuotationItem
from schemas.quotation import QuotationCreate


TAX_RATE = Decimal("0.18")


def create_quotation(db: Session, data: QuotationCreate):

    if data.valid_until < date.today():
        raise HTTPException(
            status_code=400,
            detail="Quotation validity date cannot be in the past"
        )

    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="Quotation must contain at least one item"
        )

    if data.discount_amount < 0:
        raise HTTPException(status_code=400, detail="Invalid discount")

    quotation_items = []
    subtotal = Decimal("0.00")
    item_discount_total = Decimal("0.00")

    for item in data.items:

        if item.discount_amount < 0:
            raise HTTPException(status_code=400, detail="Invalid item discount")

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.status != "Active":
            raise HTTPException(status_code=400, detail="Product is inactive")

        unit_price = Decimal(str(product.base_price))

        if item.plan_id is not None:
            plan = db.query(Plan).filter(
                Plan.id == item.plan_id
            ).first()

            if not plan or plan.product_id != product.id:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid plan for selected product"
                )

            if plan.status != "Active":
                raise HTTPException(status_code=400, detail="Plan is inactive")

            unit_price = Decimal(str(plan.price))

            if item.quantity < plan.minimum_quantity:
                raise HTTPException(
                    status_code=400,
                    detail="Quantity is below plan minimum"
                )

            if (
                plan.maximum_quantity is not None
                and item.quantity > plan.maximum_quantity
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Quantity exceeds plan maximum"
                )

        variant_price = Decimal("0.00")

        if item.variant_id is not None:
            variant = db.query(ProductVariant).filter(
                ProductVariant.id == item.variant_id
            ).first()

            if not variant or variant.product_id != product.id:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid variant for selected product"
                )

            if variant.status != "Active":
                raise HTTPException(status_code=400, detail="Variant is inactive")

            variant_price = Decimal(str(variant.additional_price))

        unit_price += variant_price

        gross = unit_price * item.quantity

        if item.discount_amount > gross:
            raise HTTPException(
                status_code=400,
                detail="Item discount cannot exceed its gross amount"
            )

        taxable_amount = gross - item.discount_amount
        item_tax = (taxable_amount * TAX_RATE).quantize(Decimal("0.01"))
        item_total = taxable_amount + item_tax

        quotation_items.append({
            "product_id": item.product_id,
            "plan_id": item.plan_id,
            "variant_id": item.variant_id,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "discount_amount": item.discount_amount,
            "tax_amount": item_tax,
            "total_amount": item_total
        })

        subtotal += gross
        item_discount_total += item.discount_amount

    if data.discount_amount > subtotal - item_discount_total:
        raise HTTPException(
            status_code=400,
            detail="Quotation discount exceeds the remaining amount"
        )

    taxable_subtotal = subtotal - item_discount_total - data.discount_amount

    total_tax = (taxable_subtotal * TAX_RATE).quantize(Decimal("0.01"))

    total_amount = taxable_subtotal + total_tax

    quotation = Quotation(
        quotation_number=f"QT-{date.today():%Y%m%d}-{uuid4().hex[:6].upper()}",
        customer_id=data.customer_id,
        created_by=data.created_by,
        quotation_date=date.today(),
        valid_until=data.valid_until,
        subtotal=subtotal,
        discount_amount=item_discount_total + data.discount_amount,
        tax_amount=total_tax,
        total_amount=total_amount,
        status="Draft",
        notes=data.notes
    )

    db.add(quotation)
    db.flush()

    for item_data in quotation_items:
        db.add(
            QuotationItem(
                quotation_id=quotation.id,
                **item_data
            )
        )

    db.commit()
    db.refresh(quotation)

    return quotation