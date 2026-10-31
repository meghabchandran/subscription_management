"""
Small demo-data loader for the Subscriptions / Invoices pages.
Safe to run more than once. Does not touch any teammate's files.

Run from the backend folder:   python demo_data.py
"""
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import inspect

from database import Base, engine, SessionLocal
import models  # noqa: F401  (registers all tables)
from models import Customer, Product, Plan, Subscription, SubscriptionItem

Base.metadata.create_all(bind=engine)


def pk_name(model):
    return inspect(model).primary_key[0].key


def make(model, **values):
    """Create a model instance using only the columns this model really has."""
    cols = {c.key for c in inspect(model).columns}
    return model(**{k: v for k, v in values.items() if k in cols})


def get_or_create_customer(db, name, email):
    obj = db.query(Customer).filter(Customer.email == email).first()
    if obj:
        return obj
    obj = make(
        Customer,
        name=name, company_name=name, contact_person=name,
        email=email, phone="9876543210", city="Kochi", state="Kerala",
        country="India", status="Active",
    )
    db.add(obj)
    db.flush()
    return obj


def get_or_create_product(db, name, code, price):
    obj = db.query(Product).filter(Product.product_code == code).first()
    if obj:
        return obj
    obj = Product(product_name=name, product_code=code, description=name,
                  category="Software", base_price=Decimal(price), status="Active")
    db.add(obj)
    db.flush()
    return obj


def get_or_create_plan(db, product, name, cycle, price):
    obj = db.query(Plan).filter(Plan.plan_name == name).first()
    if obj:
        return obj
    obj = make(
        Plan, product_id=product.id, plan_name=name, description=name,
        billing_cycle=cycle, billing_interval=1, price=Decimal(price),
        minimum_quantity=1, maximum_quantity=10, trial_days=0,
        auto_renew=True, status="Active",
    )
    db.add(obj)
    db.flush()
    return obj


def add_subscription(db, number, customer_id, cycle, next_billing, items):
    if db.query(Subscription).filter(Subscription.subscription_number == number).first():
        print(f"  {number} already exists, skipped")
        return
    today = date.today()
    sub = Subscription(
        subscription_number=number, customer_id=customer_id,
        start_date=today - timedelta(days=30),
        end_date=today + timedelta(days=335),
        billing_start_date=today - timedelta(days=30),
        next_billing_date=next_billing,
        billing_cycle=cycle, status="draft", auto_renew=True,
    )
    db.add(sub)
    db.flush()

    for product, plan, qty, discount in items:
        unit = Decimal(plan.price)
        subtotal = unit * qty
        tax = ((subtotal - discount) * Decimal("0.18")).quantize(Decimal("0.01"))
        db.add(SubscriptionItem(
            subscription_id=sub.id, product_id=product.id, plan_id=plan.id,
            quantity=qty, unit_price=unit, discount_amount=discount,
            tax_amount=tax, total_amount=subtotal - discount + tax,
        ))
    print(f"  created {number} (status: draft)")


def main():
    db = SessionLocal()
    try:
        c1 = get_or_create_customer(db, "ABC Technologies", "abc@company.com")
        c2 = get_or_create_customer(db, "Nova Solutions", "nova@company.com")
        cid1, cid2 = getattr(c1, pk_name(Customer)), getattr(c2, pk_name(Customer))

        acc = get_or_create_product(db, "Accounting Software", "ACC-001", "1000")
        crm = get_or_create_product(db, "CRM Software", "CRM-001", "1500")
        acc_plan = get_or_create_plan(db, acc, "Accounting Monthly", "Monthly", "1000")
        crm_plan = get_or_create_plan(db, crm, "CRM Monthly", "Monthly", "1500")

        today = date.today()
        add_subscription(db, "SUB-0001", cid1, "monthly", today,
                         [(acc, acc_plan, 2, Decimal("100")),
                          (crm, crm_plan, 1, Decimal("0"))])
        add_subscription(db, "SUB-0002", cid2, "monthly", today - timedelta(days=2),
                         [(crm, crm_plan, 3, Decimal("200"))])
        add_subscription(db, "SUB-0003", cid2, "yearly", today + timedelta(days=60),
                         [(acc, acc_plan, 1, Decimal("0"))])
        db.commit()
        print("Done. Refresh /subscriptions in the browser.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()