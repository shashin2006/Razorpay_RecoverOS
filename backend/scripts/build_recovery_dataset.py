import csv
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Payment, RecoveryAction, RecoveryCase
from app.ml.features import (
    build_recovery_features,
    build_recovery_target,
)


OUTPUT_FILE = Path("data/recovery_dataset.csv")


def build_dataset(db: Session):
    rows = []

    cases = (
        db.query(RecoveryCase)
        .order_by(RecoveryCase.id.asc())
        .all()
    )

    for recovery_case in cases:

        payment = (
            db.query(Payment)
            .filter(
                Payment.razorpay_payment_id
                == recovery_case.payment_id
            )
            .first()
        )

        if payment is None:
            print(
                f"Skipping RecoveryCase {recovery_case.id}: "
                f"Payment {recovery_case.payment_id} not found."
            )
            continue

        action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.recovery_case_id
                == recovery_case.id
            )
            .order_by(
                RecoveryAction.attempt_number.desc()
            )
            .first()
        )

        features = build_recovery_features(
            payment=payment,
            recovery_case=recovery_case,
            recovery_action=action,
        )

        target = build_recovery_target(
            recovery_case=recovery_case,
        )

        row = {
            **features,
            "recovered": target,
            "data_source": "real",
        }

        rows.append(row)

    return rows


def write_csv(rows):
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not rows:
        print("No recovery data found.")
        return

    fieldnames = list(rows[0].keys())

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Recovery dataset created.")
    print("File:", OUTPUT_FILE)
    print("Rows:", len(rows))

    recovered = sum(
        row["recovered"] == 1
        for row in rows
    )

    unrecovered = sum(
        row["recovered"] == 0
        for row in rows
    )

    print("Recovered:", recovered)
    print("Unrecovered:", unrecovered)


def main():
    db = SessionLocal()

    try:
        rows = build_dataset(db)
        write_csv(rows)

    finally:
        db.close()


if __name__ == "__main__":
    main()