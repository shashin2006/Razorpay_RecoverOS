from app.db.database import SessionLocal
from app.db.models import (
    MLPrediction,
    Payment,
    RecoveryAction,
    RecoveryCase,
)

from app.services.llm.recovery_context import (
    build_recovery_context,
)

from app.services.llm.recovery_analyst import (
    analyze_recovery_case,
)

from app.services.recovery_policy import (
    determine_recovery_action,
)


CASE_ID = 103


def main():

    db = SessionLocal()

    try:

        recovery_case = (
            db.query(RecoveryCase)
            .filter(
                RecoveryCase.id == CASE_ID
            )
            .first()
        )

        if recovery_case is None:
            raise RuntimeError(
                f"RecoveryCase {CASE_ID} not found."
            )

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id
                == recovery_case.payment_id
            )
            .first()
        )

        action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.recovery_case_id
                == recovery_case.id
            )
            .order_by(
                RecoveryAction.id.desc()
            )
            .first()
        )

        prediction = (
            db.query(MLPrediction)
            .filter(
                MLPrediction.recovery_case_id
                == recovery_case.id
            )
            .order_by(
                MLPrediction.id.desc()
            )
            .first()
        )

        policy = determine_recovery_action(
            recovery_case
        )

        context = build_recovery_context(
            payment=payment,
            recovery_case=recovery_case,
            recovery_action=action,
            prediction=prediction,
            policy_decision=policy,
        )

        print("=" * 70)
        print(
            "RecoveryOS NVIDIA Recovery Analyst"
        )
        print("=" * 70)

        result = analyze_recovery_case(
            context
        )

        print()
        print("LLM Analysis")
        print("-" * 70)

        for key, value in result.items():
            print(f"\n{key}:")
            print(value)

    finally:
        db.close()


if __name__ == "__main__":
    main()