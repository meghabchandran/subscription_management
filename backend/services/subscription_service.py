from datetime import datetime, date
from sqlalchemy.orm import Session

from models.subscription import Subscription
from schemas.subscription import SubscriptionCreate


def create_subscription(
    db: Session,
    subscription_data: SubscriptionCreate
):
    """Create and save a new subscription."""

    new_subscription = Subscription(
        subscription_number=subscription_data.subscription_number,
        customer_id=subscription_data.customer_id,
        quotation_id=subscription_data.quotation_id,
        start_date=subscription_data.start_date,
        end_date=subscription_data.end_date,
        billing_start_date=subscription_data.billing_start_date,
        next_billing_date=subscription_data.next_billing_date,
        billing_cycle=subscription_data.billing_cycle,
        auto_renew=subscription_data.auto_renew
    )

    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return new_subscription


def get_subscriptions(db: Session):
    """Get all subscriptions."""

    return db.query(Subscription).all()


def get_subscription_by_id(
    db: Session,
    subscription_id: int
):
    """Get one subscription by its ID."""

    return (
        db.query(Subscription)
        .filter(Subscription.id == subscription_id)
        .first()
    )

def confirm_subscription(db: Session, subscription_id: int):
    """Confirm a draft subscription."""

    subscription = get_subscription_by_id(db, subscription_id)

    if not subscription:
        return None

    subscription.status = "confirmed"

    db.commit()
    db.refresh(subscription)

    return subscription


def activate_subscription(db: Session, subscription_id: int):
    """Activate a confirmed subscription."""

    subscription = get_subscription_by_id(db, subscription_id)

    if not subscription:
        return None

    subscription.status = "active"

    db.commit()
    db.refresh(subscription)

    return subscription


def pause_subscription(db: Session, subscription_id: int):
    """Pause an active subscription."""

    subscription = get_subscription_by_id(db, subscription_id)

    if not subscription:
        return None

    subscription.status = "paused"
    subscription.paused_at = datetime.utcnow()

    db.commit()
    db.refresh(subscription)

    return subscription


def renew_subscription(
    db: Session,
    subscription_id: int,
    new_end_date: date
):
    """Renew a subscription by updating its end date."""

    subscription = get_subscription_by_id(db, subscription_id)

    if not subscription:
        return None

    subscription.end_date = new_end_date
    subscription.status = "active"
    subscription.paused_at = None

    db.commit()
    db.refresh(subscription)

    return subscription


def close_subscription(db: Session, subscription_id: int):
    """Close a subscription."""

    subscription = get_subscription_by_id(db, subscription_id)

    if not subscription:
        return None

    subscription.status = "closed"
    subscription.closed_at = datetime.utcnow()

    db.commit()
    db.refresh(subscription)

    return subscription