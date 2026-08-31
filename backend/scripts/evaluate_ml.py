from app.db.database import SessionLocal

from app.services.ml_evaluation import (
    get_ml_evaluation,
    get_probability_bucket_analysis,
    get_policy_ml_agreement,
)


def main():

    db = SessionLocal()

    try:

        evaluation = get_ml_evaluation(db)
        agreement = get_policy_ml_agreement(db)

        print()
        print("=" * 60)
        print("RecoveryOS ML Evaluation")
        print("=" * 60)

        print(
            f"Completed Predictions : "
            f"{evaluation['total_predictions']}"
        )

        print(
            f"Recovered             : "
            f"{evaluation['recovered_predictions']}"
        )

        print(
            f"Unrecovered           : "
            f"{evaluation['unrecovered_predictions']}"
        )

        print(
            f"Recovery Rate         : "
            f"{evaluation['recovery_rate'] * 100:.2f}%"
        )

        print(
            f"Revenue Recovered     : "
            f"₹{evaluation['total_revenue_recovered'] / 100:.2f}"
        )

        print()
        print("=" * 60)
        print("Probability Bucket Analysis")
        print("=" * 60)

        print(
            f"{'Bucket':<12}"
            f"{'Predictions':<15}"
            f"{'Recovered':<12}"
            f"{'Recovery %':<12}"
            f"{'Revenue':<12}"
        )

        print("-" * 60)

        buckets = get_probability_bucket_analysis(db)

        for bucket in buckets:

            print(
                f"{bucket['bucket']:<12}"
                f"{bucket['predictions']:<15}"
                f"{bucket['recovered']:<12}"
                f"{bucket['recovery_rate'] * 100:<12.2f}"
                f"₹{bucket['revenue_recovered'] / 100:.2f}"
            )

        print()

    finally:

        db.close()


if __name__ == "__main__":
    main()