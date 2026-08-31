from pathlib import Path

import pandas as pd


DATASET_PATH = Path("data/recovery_dataset.csv")


def main():

    if not DATASET_PATH.exists():
        print(
            f"Dataset not found: {DATASET_PATH}"
        )
        return

    df = pd.read_csv(DATASET_PATH)

    print()
    print("=" * 70)
    print("RecoveryOS Training Dataset Inspection")
    print("=" * 70)

    print(
        f"Rows                 : {len(df)}"
    )

    print(
        f"Columns              : {len(df.columns)}"
    )

    print()

    print("Columns:")
    print("-" * 70)

    for column in df.columns:
        print(f"- {column}")

    print()

    print("Failure Category Distribution")
    print("-" * 70)

    if "failure_category" in df.columns:

        print(
            df["failure_category"]
            .value_counts()
        )

    print()

    print("Target Distribution")
    print("-" * 70)

    if "recovered" in df.columns:

        print(
            df["recovered"]
            .value_counts()
        )

    elif "actual_recovery" in df.columns:

        print(
            df["actual_recovery"]
            .value_counts()
        )

    print()

    print("Payment Method Distribution")
    print("-" * 70)

    if "payment_method" in df.columns:

        print(
            df["payment_method"]
            .value_counts()
        )

    elif "method" in df.columns:

        print(
            df["method"]
            .value_counts()
        )

    print()

    print("Action Distribution")
    print("-" * 70)

    if "action_type" in df.columns:

        print(
            df["action_type"]
            .value_counts()
        )

    print()

    print("Numeric Feature Summary")
    print("-" * 70)

    print(
        df.describe(include="all").transpose()
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()