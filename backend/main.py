
from fastapi import FastAPI

from database import engine
from models.product import Product
from models.product_variant import ProductVariant
from models.plan import Plan

from routes import (
    product_routes,
    variant_routes,
    plan_routes,
    quotation_routes
)

app = FastAPI(
    title="Brightloop Subscription Management API",
    description="Product, Plan and Quotation Management",
    version="1.0.0"
)

@app.on_event("startup")
def create_tables():
    Product.__table__.create(bind=engine, checkfirst=True)
    ProductVariant.__table__.create(bind=engine, checkfirst=True)
    Plan.__table__.create(bind=engine, checkfirst=True)



@app.get("/")
def read_root():
    return {
        "message": "Brightloop Backend is running!"
    }


# Register Member 2 routes
app.include_router(product_routes.router)
app.include_router(variant_routes.router)
app.include_router(plan_routes.router)
app.include_router(quotation_routes.router)
