from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse
)
from services.subscription_service import (
    create_subscription,
    get_subscriptions,
    get_subscription_by_id,
    confirm_subscription,
    activate_subscription,
    pause_subscription,
    renew_subscription,
    close_subscription
)
from datetime import date


router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
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
    response_model=SubscriptionResponse
)
def create_new_subscription(
    subscription_data: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    return create_subscription(db, subscription_data)


@router.get(
    "/",
    response_model=List[SubscriptionResponse]
)
def read_subscriptions(
    db: Session = Depends(get_db)
):
    return get_subscriptions(db)


@router.get(
    "/{subscription_id}",
    response_model=SubscriptionResponse
)
def read_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = get_subscription_by_id(
        db,
        subscription_id
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    return subscription

@router.post(
    "/{subscription_id}/confirm",
    response_model=SubscriptionResponse
)
def confirm_existing_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = confirm_subscription(
        db,
        subscription_id
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    return subscription


@router.post(
    "/{subscription_id}/activate",
    response_model=SubscriptionResponse
)
def activate_existing_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = activate_subscription(
        db,
        subscription_id
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    return subscription


@router.post(
    "/{subscription_id}/pause",
    response_model=SubscriptionResponse
)
def pause_existing_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = pause_subscription(
        db,
        subscription_id
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    return subscription


@router.post(
    "/{subscription_id}/renew",
    response_model=SubscriptionResponse
)
def renew_existing_subscription(
    subscription_id: int,
    new_end_date: date,
    db: Session = Depends(get_db)
):
    subscription = renew_subscription(
        db,
        subscription_id,
        new_end_date
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    return subscription


@router.post(
    "/{subscription_id}/close",
    response_model=SubscriptionResponse
)
def close_existing_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = close_subscription(
        db,
        subscription_id
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    return subscription