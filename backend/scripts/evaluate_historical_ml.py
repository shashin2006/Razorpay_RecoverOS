from sqlalchemy.orm import Session
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from app.db.database import SessionLocal
from app.db.models import (
    Payment,
    RecoveryAction,
    RecoveryCase,
)
from app.ml.features import build_recovery_features
from app.ml.predictor import predict_recovery


def load_evaluation_data(db: Session):

    rows = (
        db.query(RecoveryCase, Payment)
        .join(
            Payment,
            Payment.razorpay_payment_id
            == RecoveryCase.payment_id,
        )
        .order_by(RecoveryCase.id)
        .all()
    )

    return rows


def get_recovery_action(
    db: Session,
    recovery_case_id: int,
) -> RecoveryAction | None:

    return (
        db.query(RecoveryAction)
        .filter(
            RecoveryAction.recovery_case_id
            == recovery_case_id
        )
        .order_by(RecoveryAction.id.desc())
        .first()
    )


def main():

    db = SessionLocal()

    try:

        rows = load_evaluation_data(db)

        if not rows:
            print("No evaluation data available.")
            return

        y_true = []
        y_pred = []
        probabilities = []

        print()
        print("=" * 70)
        print("RecoveryOS Historical ML Evaluation")
        print("=" * 70)

        for recovery_case, payment in rows:

            # ----------------------------------------
            # ACTUAL OUTCOME
            # ----------------------------------------

            actual = (
                1
                if recovery_case.amount_recovered > 0
                else 0
            )

            # ----------------------------------------
            # RECOVERY ACTION
            # ----------------------------------------

            recovery_action = get_recovery_action(
                db=db,
                recovery_case_id=recovery_case.id,
            )

            # ----------------------------------------
            # BUILD FEATURES
            # ----------------------------------------

            features = build_recovery_features(
                payment=payment,
                recovery_case=recovery_case,
                recovery_action=recovery_action,
            )

            # ----------------------------------------
            # MODEL PREDICTION
            # ----------------------------------------

            prediction = predict_recovery(
                features=features,
            )

            probability = prediction.probability

            predicted = (
                1
                if prediction.recommends_recovery
                else 0
            )

            # ----------------------------------------
            # STORE RESULTS
            # ----------------------------------------

            y_true.append(actual)
            y_pred.append(predicted)
            probabilities.append(probability)

            print(
                f"Case {recovery_case.id:<5} "
                f"Probability={probability:.4f} "
                f"Predicted={predicted} "
                f"Actual={actual}"
            )

        # ----------------------------------------
        # SUMMARY
        # ----------------------------------------

        print()
        print("-" * 70)

        print(
            f"Evaluation samples : {len(y_true)}"
        )

        print(
            f"Actual recovered   : {sum(y_true)}"
        )

        print(
            f"Actual unrecovered : "
            f"{len(y_true) - sum(y_true)}"
        )

        print()

        print(
            f"Accuracy  : "
            f"{accuracy_score(y_true, y_pred):.4f}"
        )

        print(
            f"Precision : "
            f"{precision_score(y_true, y_pred, zero_division=0):.4f}"
        )

        print(
            f"Recall    : "
            f"{recall_score(y_true, y_pred, zero_division=0):.4f}"
        )

        print(
            f"F1        : "
            f"{f1_score(y_true, y_pred, zero_division=0):.4f}"
        )

        if len(set(y_true)) == 2:

            print(
                f"ROC-AUC   : "
                f"{roc_auc_score(y_true, probabilities):.4f}"
            )

        else:

            print(
                "ROC-AUC   : not available "
                "(only one outcome class)"
            )

        print()
        print("=" * 70)

    finally:

        db.close()


if __name__ == "__main__":
    main()