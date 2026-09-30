import uuid
from app.db.database import SessionLocal
from app.db.models import Payment
from app.services.event_processor import process_webhook_event

PAYMENT_ID = f"pay_test_{uuid.uuid4().hex}"
ORDER_ID = f"order_test_{uuid.uuid4().hex}"


def test_failed_to_captured_transition():

    db = SessionLocal()

    try:

        db.query(Payment).filter(
            Payment.razorpay_payment_id == PAYMENT_ID
        ).delete()

        db.commit()

        # --------------------------------------------------
        # EVENT 1: payment.failed
        # --------------------------------------------------

        failed_payload = {
            "event": "payment.failed",
            "entity": "event",
            "payload": {
                "payment": {
                    "entity": {
                        "id": PAYMENT_ID,
                        "order_id": ORDER_ID,
                        "amount": 50000,
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

        process_webhook_event(
            db=db,
            event_type="payment.failed",
            payload=failed_payload,
        )

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id == PAYMENT_ID
            )
            .first()
        )

        assert payment is not None
        assert payment.status == "failed"

        print("\nAfter payment.failed:")
        print("Payment ID:", payment.razorpay_payment_id)
        print("Status:", payment.status)

        # --------------------------------------------------
        # EVENT 2: payment.captured
        # --------------------------------------------------

        captured_payload = {
            "event": "payment.captured",
            "entity": "event",
            "payload": {
                "payment": {
                    "entity": {
                        "id": PAYMENT_ID,
                        "order_id": ORDER_ID,
                        "amount": 50000,
                        "currency": "INR",
                        "method": "netbanking",
                        "status": "captured",
                        "captured": True,
                        "created_at": 1788104210,
                        "error_code": None,
                        "error_step": None,
                        "error_reason": None,
                        "error_source": None,
                        "error_description": None,
                    }
                }
            },
        }

        process_webhook_event(
            db=db,
            event_type="payment.captured",
            payload=captured_payload,
        )

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id == PAYMENT_ID
            )
            .first()
        )

        assert payment is not None
        assert payment.status == "captured"

        print("\nAfter payment.captured:")
        print("Payment ID:", payment.razorpay_payment_id)
        print("Status:", payment.status)


        count = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id == PAYMENT_ID
            )
            .count()
        )

        assert count == 1

        print("\nPayment count:", count)

    finally:

        db.query(Payment).filter(
            Payment.razorpay_payment_id == PAYMENT_ID
        ).delete()

        db.commit()
        db.close()

def test_captured_payment_cannot_move_back_to_failed():

    db = SessionLocal()

    payment_id = "pay_state_test_002"
    order_id = "order_state_test_002"

    try:
        # Clean previous test data
        db.query(Payment).filter(
            Payment.razorpay_payment_id == payment_id
        ).delete()

        db.commit()

        # --------------------------------------------------
        # First: payment.captured
        # --------------------------------------------------

        captured_payload = {
            "event": "payment.captured",
            "entity": "event",
            "payload": {
                "payment": {
                    "entity": {
                        "id": payment_id,
                        "order_id": order_id,
                        "amount": 50000,
                        "currency": "INR",
                        "method": "netbanking",
                        "status": "captured",
                        "captured": True,
                        "created_at": 1788104210,
                        "error_code": None,
                        "error_step": None,
                        "error_reason": None,
                        "error_source": None,
                        "error_description": None,
                    }
                }
            },
        }

        process_webhook_event(
            db=db,
            event_type="payment.captured",
            payload=captured_payload,
        )

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id == payment_id
            )
            .first()
        )

        assert payment.status == "captured"

        # --------------------------------------------------
        # Then: stale payment.failed
        # --------------------------------------------------

        failed_payload = {
            "event": "payment.failed",
            "entity": "event",
            "payload": {
                "payment": {
                    "entity": {
                        "id": payment_id,
                        "order_id": order_id,
                        "amount": 50000,
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

        process_webhook_event(
            db=db,
            event_type="payment.failed",
            payload=failed_payload,
        )

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id == payment_id
            )
            .first()
        )

        print("\nAfter stale payment.failed:")
        print("Status:", payment.status)

        # This SHOULD remain captured.
        assert payment.status == "captured"

    finally:
        db.query(Payment).filter(
            Payment.razorpay_payment_id == payment_id
        ).delete()

        db.commit()
        db.close()