from app.db.database import SessionLocal
from app.db.models import WebhookEvent
from app.services.event_processor import process_webhook_event


EVENT_ID = "TWHormks2XJbmp"


db = SessionLocal()

try:

    event = (
        db.query(WebhookEvent)
        .filter(
            WebhookEvent.razorpay_event_id == EVENT_ID
        )
        .first()
    )

    if event is None:
        raise RuntimeError(
            f"Webhook event {EVENT_ID} not found"
        )

    print("Found event:")
    print("Event ID:", event.razorpay_event_id)
    print("Event type:", event.event_type)

    process_webhook_event(
        db=db,
        event_type=event.event_type,
        payload=event.payload,
    )

    event.processed = True
    db.commit()

    print("Event processed successfully.")

finally:
    db.close()