from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

from routes import auth

from routes import (
    product_routes,
    variant_routes,
    plan_routes,
    quotation_routes,
    subscriptions,
    invoices,
    taxes
)


# Initialize FastAPI application
app = FastAPI(
    title="Brightloop Subscription Management API"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Brightloop Backend is running!"
    }


# Authentication routes
app.include_router(auth.router)


# Member 2 - Product, Variant, Plan and Quotation routes
app.include_router(product_routes.router)
app.include_router(variant_routes.router)
app.include_router(plan_routes.router)
app.include_router(quotation_routes.router)


# Member 3 - Subscription and Invoice routes
app.include_router(subscriptions.router)
app.include_router(invoices.router)
app.include_router(taxes.router)