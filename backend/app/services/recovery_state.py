from enum import Enum


class RecoveryStatus(str, Enum):
    OPEN = "open"
    ACTION_PENDING = "action_pending"
    AWAITING_CUSTOMER = "awaiting_customer"
    RECOVERED = "recovered"
    ESCALATED = "escalated"
    EXPIRED = "expired"


def is_valid_recovery_transition(
    current_status: str,
    new_status: str,
) -> bool:

    if current_status == new_status:
        return True

    allowed_transitions = {
        RecoveryStatus.OPEN: {
            RecoveryStatus.ACTION_PENDING,
            RecoveryStatus.EXPIRED,
            RecoveryStatus.ESCALATED,
        },

        RecoveryStatus.ACTION_PENDING: {
            RecoveryStatus.AWAITING_CUSTOMER,
            RecoveryStatus.RECOVERED,
            RecoveryStatus.ESCALATED,
        },

        RecoveryStatus.AWAITING_CUSTOMER: {
            RecoveryStatus.RECOVERED,
            RecoveryStatus.ESCALATED,
            RecoveryStatus.EXPIRED,
        },

        RecoveryStatus.RECOVERED: set(),

        RecoveryStatus.ESCALATED: set(),

        RecoveryStatus.EXPIRED: set(),
    }

    try:
        current = RecoveryStatus(current_status)
        new = RecoveryStatus(new_status)
    except ValueError:
        return False

    return new in allowed_transitions.get(
        current,
        set(),
    )