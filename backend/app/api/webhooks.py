import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import WebhookEvent
from app.services.event_processor import process_webhook_event


router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.body()

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    event_id = payload.get("id")
    event_type = payload.get("type")

    if not event_id:
        raise HTTPException(status_code=400, detail="Missing Stripe event ID")
    if not event_type:
        raise HTTPException(status_code=400, detail="Missing Stripe event type")

    statement = (
        insert(WebhookEvent)
        .values(
            provider_event_id=event_id,
            event_type=event_type,
            payload=payload,
            # Local Stripe CLI development intentionally skips signature
            # verification. Production deployments must verify signatures.
            signature_valid=True,
            processed=False,
        )
        .on_conflict_do_nothing(index_elements=["provider_event_id"])
        .returning(WebhookEvent.id)
    )

    inserted_id = db.execute(statement).scalar_one_or_none()
    db.commit()

    if inserted_id is None:
        return {"status": "duplicate", "event_id": event_id}

    try:
        process_webhook_event(
            db=db,
            event_type=event_type,
            payload=payload,
        )

        db.query(WebhookEvent).filter(
            WebhookEvent.id == inserted_id
        ).update({"processed": True})
        db.commit()

        return {
            "status": "accepted",
            "event_id": event_id,
            "event_type": event_type,
        }
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed",
        ) from exc


@router.get("/events")
async def get_webhook_events(db: Session = Depends(get_db)):
    result = db.execute(
        select(WebhookEvent)
        .order_by(WebhookEvent.id.desc())
        .limit(50)
    )
    events = result.scalars().all()

    return [
        {
            "id": event.id,
            "provider_event_id": event.provider_event_id,
            "event_type": event.event_type,
            "processed": event.processed,
            "received_at": event.received_at,
        }
        for event in events
    ]
