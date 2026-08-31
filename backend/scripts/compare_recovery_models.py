import pandas as pd

from sklearn.model_selection import train_test_split

from app.ml.model import (
    build_model,
    build_random_forest_model,
    evaluate_model,
)


DATASET = (
    "data/recovery_dataset_synthetic.csv"
)


TARGET = "recovered"


EXCLUDED_COLUMNS = {
    "recovered",
    "amount_recovered",
    "data_source",
}


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

    # ----------------------------------------
    # Logistic Regression
    # ----------------------------------------

    logistic_model = build_model()

    logistic_metrics = evaluate_model(
        logistic_model,
        X_train,
        X_test,
        y_train,
        y_test,
    )

    # ----------------------------------------
    # Random Forest
    # ----------------------------------------

    random_forest_model = (
        build_random_forest_model()
    )

    random_forest_metrics = evaluate_model(
        random_forest_model,
        X_train,
        X_test,
        y_train,
        y_test,
    )

    # ----------------------------------------
    # Results
    # ----------------------------------------

    print("\nModel Comparison")
    print("=" * 60)

    print("\nLogistic Regression:")

    for name, value in logistic_metrics.items():
        print(
            f"{name:10}: {value:.4f}"
        )

    print("\nRandom Forest:")

    for name, value in random_forest_metrics.items():
        print(
            f"{name:10}: {value:.4f}"
        )

    print("\nROC-AUC comparison:")

    print(
        f"Logistic Regression: "
        f"{logistic_metrics['roc_auc']:.4f}"
    )

    print(
        f"Random Forest:       "
        f"{random_forest_metrics['roc_auc']:.4f}"
    )


if __name__ == "__main__":
    main()