from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    Payment,
    RecoveryCase,
)

from app.services.action_executor import (
    execute_recovery_action,
)

from app.services.failure_classifier import (
    classify_failure,
    Recoverability,
)

from app.services.ml_decision_service import (
    evaluate_ml_against_policy,
)


MAX_RECOVERY_ATTEMPTS = 3


def create_recovery_case(
    db: Session,
    payment: Payment,
    classification,
) -> RecoveryCase:

    existing_case = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.payment_id
            == payment.razorpay_payment_id
        )
        .first()
    )

    if existing_case is not None:
        return existing_case

    recovery_case = RecoveryCase(
        payment_id=payment.razorpay_payment_id,
        amount_at_risk_minor=payment.amount_minor,
        amount_recovered=0,
        currency=payment.currency,
        failure_category=classification.category.value,
        status="open",
        attempts=0,
    )

    db.add(recovery_case)
    db.commit()
    db.refresh(recovery_case)

    return recovery_case


def orchestrate_payment_failure(
    db: Session,
    payment: Payment,
    payment_data: dict[str, Any],
):

    classification = classify_failure(
        payment_data
    )

    # ----------------------------------------
    # NOT RECOVERABLE
    # ----------------------------------------

    if (
        classification.recoverability
        != Recoverability.RECOVERABLE
    ):
        return {
            "status": "not_recoverable",
            "category": classification.category.value,
            "reason": classification.reason,
        }

    # ----------------------------------------
    # CREATE / GET RECOVERY CASE
    # ----------------------------------------

    recovery_case = create_recovery_case(
        db=db,
        payment=payment,
        classification=classification,
    )

    # ----------------------------------------
    # ML SHADOW + POLICY COMPARISON
    # ----------------------------------------

    ml_decision = evaluate_ml_against_policy(
        db=db,
        payment=payment,
        recovery_case=recovery_case,
    )

    # ----------------------------------------
    # SELECT EXISTING BOUNDED ACTION
    # ----------------------------------------

    action = "alternate_payment_method"

    # ----------------------------------------
    # EXECUTE EXISTING RECOVERY ACTION
    # ----------------------------------------

    result = execute_recovery_action(
        db=db,
        recovery_case=recovery_case,
        action=action,
        reason=classification.reason,
        max_attempts=MAX_RECOVERY_ATTEMPTS,
    )

    # ----------------------------------------
    # RETURN EXISTING RECOVERY RESULT
    # ----------------------------------------

    return {
        "status": result.status.value,
        "category": classification.category.value,
        "action": result.action,
        "external_id": result.external_id,
        "payment_link_url": result.payment_link_url,
        "message": result.message,
    }