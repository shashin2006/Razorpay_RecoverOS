from app.db.database import SessionLocal
from app.db.models import RecoveryCase
from app.services.action_executor import execute_recovery_action


CASE_ID = 29


db = SessionLocal()

try:

    case = (
        db.query(RecoveryCase)
        .filter(RecoveryCase.id == CASE_ID)
        .first()
    )

    if case is None:
        raise RuntimeError(
            f"Recovery Case {CASE_ID} not found"
        )

    print("Recovery Case found:")
    print("ID:", case.id)
    print("Payment ID:", case.payment_id)
    print("Amount at risk:", case.amount_at_risk_minor)
    print("Status:", case.status)
    print("Attempts:", case.attempts)

    result = execute_recovery_action(
        db=db,
        recovery_case=case,
        action="alternate_payment_method",
        reason="Bank declined the original payment.",
        max_attempts=3,
    )

    print("\nExecution result:")
    print("Status:", result.status)
    print("Action:", result.action)
    print("External ID:", result.external_id)
    print("Payment Link:", result.payment_link_url)
    print("Message:", result.message)

finally:
    db.close()