from app.db.database import SessionLocal
from app.db.models import RecoveryCase


db = SessionLocal()

try:
    case = RecoveryCase(
        payment_id="pay_e2e_test_001",
        amount_at_risk_minor=50000,
        currency="INR",
        failure_category="bank_decline",
        status="open",
        attempts=0,
        amount_recovered=0,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    print("Recovery Case created:")
    print("ID:", case.id)
    print("Payment ID:", case.payment_id)
    print("Amount at risk:", case.amount_at_risk_minor)
    print("Currency:", case.currency)
    print("Failure category:", case.failure_category)
    print("Status:", case.status)
    print("Attempts:", case.attempts)

finally:
    db.close()  