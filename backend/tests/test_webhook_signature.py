import hashlib
import hmac

from app.services.razorpay_webhook import verify_webhook_signature


def test_valid_signature():
    body = b'{"event":"payment.failed"}'
    secret = "test-secret"

    signature = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    assert verify_webhook_signature(
        body,
        signature,
        secret,
    )


def test_invalid_signature():
    body = b'{"event":"payment.failed"}'
    secret = "test-secret"

    assert not verify_webhook_signature(
        body,
        "invalid-signature",
        secret,
    )