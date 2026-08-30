import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import WebhookEvent
from app.services.razorpay_webhook import verify_webhook_signature
from sqlalchemy import select
from app.services.event_processor import process_webhook_event  

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"],
)


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.body()

    received_signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    if not received_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay webhook signature",
        )

    is_valid = verify_webhook_signature(
        body=body,
        received_signature=received_signature,
        secret=settings.razorpay_webhook_secret,
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay webhook signature",
        )

    event_id = request.headers.get(
        "x-razorpay-event-id"
    )

    if not event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay event ID",
        )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        )

    event_type = payload.get("event")

    if not event_type:
        raise HTTPException(
            status_code=400,
            detail="Missing event type",
        )

    logger.info(
        "Received Razorpay webhook event_id=%s event_type=%s",
        event_id,
        event_type,
    )

    statement = (
        insert(WebhookEvent)
        .values(
            razorpay_event_id=event_id,
            event_type=event_type,
            payload=payload,
            signature_valid=True,
            processed=False,
        )
        .on_conflict_do_nothing(
            index_elements=["razorpay_event_id"]
        )
        .returning(WebhookEvent.id)
    )

    result = db.execute(statement)

    inserted_id = result.scalar_one_or_none()

    db.commit()

    if inserted_id is None:
        logger.info(
            "Duplicate Razorpay webhook event_id=%s",
            event_id,
        )

        return {
            "status": "duplicate",
            "event_id": event_id,
        }
    
    process_webhook_event(
        db=db,
        event_type=event_type,
        payload=payload,
    )

    return {
        "status": "accepted",
        "event_id": event_id,
        "event_type": event_type,
    }

@router.get("/events")
async def get_webhook_events(
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(WebhookEvent)
        .order_by(WebhookEvent.id.desc())
        .limit(50)
    )

    events = result.scalars().all()

    return [
        {
            "id": event.id,
            "razorpay_event_id": event.razorpay_event_id,
            "event_type": event.event_type,
            "processed": event.processed,
            "received_at": event.received_at,
        }
        for event in events
    ]
