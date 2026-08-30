import hashlib
import hmac
import json
import uuid

import httpx


BASE_URL = "http://127.0.0.1:8000"

WEBHOOK_SECRET = "test-webhook-secret"


def create_signature(body: bytes) -> str:
    return hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()


def test_duplicate_webhook():

    payload = {
        "entity": "event",
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_001",
                    "order_id": "order_test_001",
                    "amount": 249900,
                    "currency": "INR",
                    "method": "netbanking",
                    "status": "failed",
                    "created_at": 1788104210,
                    "error_code": "BAD_REQUEST_ERROR",
                    "error_step": "payment_authorization",
                    "error_reason": "payment_failed",
                    "error_source": "bank",
                    "error_description": "Bank declined payment.",
                }
            }
        },
    }

    body = json.dumps(payload).encode("utf-8")

    signature = create_signature(body)

    # Generate a NEW event ID for every test run
    event_id = f"evt_test_{uuid.uuid4().hex}"

    headers = {
        "X-Razorpay-Signature": signature,
        "x-razorpay-event-id": event_id,
        "Content-Type": "application/json",
    }

    with httpx.Client() as client:

        # First delivery
        response_1 = client.post(
            f"{BASE_URL}/api/webhooks/razorpay",
            content=body,
            headers=headers,
        )

        print("\nFirst response:")
        print("Status:", response_1.status_code)
        print("Headers:", response_1.headers)
        print("Body:", response_1.text)

        # Second delivery - SAME EVENT
        response_2 = client.post(
            f"{BASE_URL}/api/webhooks/razorpay",
            content=body,
            headers=headers,
        )

        print("\nSecond response:")
        print("Status:", response_2.status_code)
        print("Headers:", response_2.headers)   
        print("Body:", response_2.text)

    assert response_1.status_code == 200
    assert response_2.status_code == 200

    assert response_1.json()["status"] == "accepted"
    assert response_2.json()["status"] == "duplicate"