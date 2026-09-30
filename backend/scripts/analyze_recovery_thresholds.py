import pandas as pd

from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from app.ml.model import (
    build_model,
)


DATASET = "data/recovery_dataset_synthetic.csv"


TARGET = "recovered"


EXCLUDED_COLUMNS = {
    "recovered",
    "amount_recovered",
    "data_source",
}


THRESHOLDS = [
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
]


def main():

    df = pd.read_csv(DATASET)

    X = df.drop(
        columns=list(EXCLUDED_COLUMNS),
        errors="ignore",
    )

    y = df[TARGET]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )
    )

    model = build_model()

    model.fit(
        X_train,
        y_train,
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    print("\nRecovery Threshold Analysis")
    print("=" * 80)

    print(
        f"{'Threshold':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"
        f"{'F1':<12}"
        f"{'Recovery %':<15}"
    )

    print("-" * 80)

    for threshold in THRESHOLDS:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            y_test,
            predictions,
            zero_division=0,
        )

        recall = recall_score(
            y_test,
            predictions,
            zero_division=0,
        )

        f1 = f1_score(
            y_test,
            predictions,
            zero_division=0,
        )

        predicted_recovery_rate = (
            predictions.mean() * 100
        )

        print(
            f"{threshold:<12.2f}"
            f"{precision:<12.4f}"
            f"{recall:<12.4f}"
            f"{f1:<12.4f}"
            f"{predicted_recovery_rate:<15.2f}"
        )


if __name__ == "__main__":
    main()