from fastapi import FastAPI

from database import Base, engine
import models

from routes import auth

from routes import (
    product_routes,
    variant_routes,
    plan_routes,
    quotation_routes
)


# Create all database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Brightloop Subscription Management API"
)


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