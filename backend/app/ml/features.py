from typing import Any

from app.db.models import (
    Payment,
    RecoveryAction,
    RecoveryCase,
)


def build_recovery_features(
    payment: Payment,
    recovery_case: RecoveryCase,
    recovery_action: RecoveryAction | None = None,
) -> dict[str, Any]:
    """
    Convert RecoveryOS payment and recovery data
    into ML-ready features.

    This function does not perform prediction.
    It only prepares the input data for the model.
    """

    features = {
        # Payment features
        "amount_minor": payment.amount_minor,
        "currency": payment.currency,
        "payment_method": payment.method,

        # Failure features
        "failure_category": recovery_case.failure_category,
        "error_source": payment.error_source,
        "error_step": payment.error_step,
        "error_reason": payment.error_reason,
        "error_code": payment.error_code,

        # Recovery features
        "attempts": recovery_case.attempts,
    }

    # Action information may not exist yet.
    if recovery_action is not None:
        features["action_type"] = (
            recovery_action.action_type
        )
        features["attempt_number"] = (
            recovery_action.attempt_number
        )
    else:
        features["action_type"] = None
        features["attempt_number"] = 0

    return features


def build_recovery_target(
    recovery_case: RecoveryCase,
) -> int:
    """
    Build the supervised-learning target.

    1 = recovery succeeded
    0 = recovery did not succeed
    """

    if recovery_case.amount_recovered > 0:
        return 1

    return 0