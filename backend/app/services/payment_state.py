from enum import Enum


class PaymentStatus(str, Enum):
    FAILED = "failed"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"


def is_valid_transition(
    current_status: str,
    new_status: str,
) -> bool:

    # Same state is always safe.
    if current_status == new_status:
        return True

    allowed_transitions = {
        PaymentStatus.FAILED: {
            PaymentStatus.AUTHORIZED,
            PaymentStatus.CAPTURED,
        },
        PaymentStatus.AUTHORIZED: {
            PaymentStatus.CAPTURED,
        },
        PaymentStatus.CAPTURED: set(),
    }

    try:
        current = PaymentStatus(current_status)
        new = PaymentStatus(new_status)
    except ValueError:
        return False

    return new in allowed_transitions.get(current, set())