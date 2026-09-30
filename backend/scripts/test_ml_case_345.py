from app.db.database import SessionLocal
from app.db.models import Payment, RecoveryCase
from app.services.ml_decision_service import evaluate_ml_against_policy

db = SessionLocal()

try:
    payment = db.query(Payment).filter(
        Payment.razorpay_payment_id == "pay_e2e_agent_001"
    ).first()

    recovery_case = db.query(RecoveryCase).filter(
        RecoveryCase.id == 345
    ).first()

    if not payment:
        raise RuntimeError("Payment pay_e2e_agent_001 not found")

    if not recovery_case:
        raise RuntimeError("RecoveryCase 345 not found")

    result = evaluate_ml_against_policy(
        db=db,
        payment=payment,
        recovery_case=recovery_case,
    )

    print("\n=== ML DECISION ===")
    print(f"Policy eligible : {result.policy_eligible}")
    print(f"Policy action   : {result.policy_action}")
    print(f"ML probability  : {result.ml_probability:.4f}")
    print(f"ML recommendation: {result.ml_recommendation}")
    print(f"Threshold       : {result.threshold:.2f}")
    print(f"Agreement       : {result.agreement}")

finally:
    db.close()
