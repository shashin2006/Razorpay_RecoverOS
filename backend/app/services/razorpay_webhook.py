import hmac
import hashlib


def verify_webhook_signature(
    body: bytes,
    received_signature: str,
    secret: str,
) -> bool:
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        received_signature,
    )