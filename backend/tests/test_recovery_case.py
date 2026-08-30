from app.db.database import SessionLocal
from app.db.models import RecoveryCase

from app.services.failure_classifier import (
    FailureCategory,
    FailureClassification,
    Recoverability,
)

from app.services.recovery_case import (
    create_recovery_case,
)


def test_create_recovery_case():

    db = SessionLocal()

    payment_id = "pay_recovery_test_001"

    try:

        db.query(RecoveryCase).filter(
            RecoveryCase.payment_id == payment_id
        ).delete()

        db.commit()

        classification = FailureClassification(
            category=FailureCategory.BANK_DECLINE,
            recoverability=Recoverability.RECOVERABLE,
            customer_action_required=True,
            reason="Bank declined payment.",
        )

        case = create_recovery_case(
            db=db,
            payment_id=payment_id,
            amount_at_risk_minor=50000,
            currency="INR",
            classification=classification,
        )

        assert case.payment_id == payment_id
        assert case.amount_at_risk_minor == 50000
        assert case.currency == "INR"
        assert case.failure_category == "bank_decline"
        assert case.status == "open"
        assert case.attempts == 0

    finally:

        db.query(RecoveryCase).filter(
            RecoveryCase.payment_id == payment_id
        ).delete()

        db.commit()
        db.close()

def test_duplicate_recovery_case_returns_existing_case():

    db = SessionLocal()

    payment_id = "pay_recovery_test_002"

    try:

        db.query(RecoveryCase).filter(
            RecoveryCase.payment_id == payment_id
        ).delete()

        db.commit()

        classification = FailureClassification(
            category=FailureCategory.BANK_DECLINE,
            recoverability=Recoverability.RECOVERABLE,
            customer_action_required=True,
            reason="Bank declined payment.",
        )

        case_1 = create_recovery_case(
            db=db,
            payment_id=payment_id,
            amount_at_risk_minor=50000,
            currency="INR",
            classification=classification,
        )

        case_2 = create_recovery_case(
            db=db,
            payment_id=payment_id,
            amount_at_risk_minor=50000,
            currency="INR",
            classification=classification,
        )

        assert case_1.id == case_2.id

        count = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.payment_id == payment_id
            )
            .count()
        )

        assert count == 1

    finally:

        db.query(RecoveryCase).filter(
            RecoveryCase.payment_id == payment_id
        ).delete()

        db.commit()
        db.close()