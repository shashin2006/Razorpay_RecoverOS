from enum import Enum
from dataclasses import dataclass


class FailureCategory(str, Enum):
    BANK_DECLINE = "bank_decline"
    CUSTOMER_ACTION_REQUIRED = "customer_action_required"
    PAYMENT_PROCESSING_ERROR = "payment_processing_error"
    UNKNOWN = "unknown"


class Recoverability(str, Enum):
    RECOVERABLE = "recoverable"
    NOT_RECOVERABLE = "not_recoverable"
    CUSTOMER_ACTION_REQUIRED = "customer_action_required"
    UNKNOWN = "unknown"

@dataclass
class FailureClassification:
    category: FailureCategory
    recoverability: Recoverability
    customer_action_required: bool
    reason: str

def classify_failure(payment: dict) -> FailureClassification:

    error_source = payment.get("error_source")
    error_step = payment.get("error_step")
    error_reason = payment.get("error_reason")
    error_code = payment.get("error_code")

    if (
        error_source == "bank"
        and error_step == "payment_authorization"
        and error_reason == "payment_failed"
    ):
        return FailureClassification(
            category=FailureCategory.BANK_DECLINE,
            recoverability=Recoverability.RECOVERABLE,
            customer_action_required=True,
            reason=(
                "Payment was declined by the bank "
                "during authorization."
            ),
        )

    return FailureClassification(
        category=FailureCategory.UNKNOWN,
        recoverability=Recoverability.UNKNOWN,
        customer_action_required=False,
        reason=(
            f"Unrecognized payment failure: "
            f"source={error_source}, "
            f"step={error_step}, "
            f"reason={error_reason}, "
            f"code={error_code}"
        ),
    )