import json
import uuid

import httpx


BASE_URL = "http://127.0.0.1:8000"


def test_duplicate_stripe_webhook():
    payload = {
        "id": f"evt_test_{uuid.uuid4().hex}",
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": f"pi_test_{uuid.uuid4().hex}",
                "amount": 249900,
                "currency": "inr",
                "payment_method_types": ["card"],
                "status": "requires_payment_method",
                "last_payment_error": {
                    "code": "card_declined",
                    "decline_code": "generic_decline",
                    "message": "Card declined.",
                },
                "created": 1788104210,
            }
        },
    }

    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    with httpx.Client() as client:
        response_1 = client.post(
            f"{BASE_URL}/api/webhooks/stripe",
            content=body,
            headers=headers,
        )
        response_2 = client.post(
            f"{BASE_URL}/api/webhooks/stripe",
            content=body,
            headers=headers,
        )

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_1.json()["status"] == "accepted"
    assert response_2.json()["status"] == "duplicate"
