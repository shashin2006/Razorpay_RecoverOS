from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


MODEL_FILE = Path("models/recovery_model.joblib")


TARGET = "recovered"

EXCLUDED_COLUMNS = {
    "recovered",
    "amount_recovered",
    "data_source",
}


CATEGORICAL_FEATURES = [
    "currency",
    "payment_method",
    "failure_category",
    "error_source",
    "error_step",
    "error_reason",
    "error_code",
    "action_type",
]


NUMERIC_FEATURES = [
    "amount_minor",
    "attempts",
    "attempt_number",
]


def build_model() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES,
            ),
        ]
    )

    classifier = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def train_model(
    dataset_path: str,
):
    df = pd.read_csv(dataset_path)

    if TARGET not in df.columns:
        raise ValueError(
            "Dataset does not contain target column."
        )

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

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(
            y_test,
            predictions,
        ),
        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "roc_auc": roc_auc_score(
            y_test,
            probabilities,
        ),
    }

    print("\nClassification Report:\n")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    print("Metrics:")
    for name, value in metrics.items():
        print(
            f"{name}: {value:.4f}"
        )

    return model, metrics

def build_random_forest_model() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "numeric",
                "passthrough",
                NUMERIC_FEATURES,
            ),
        ]
    )

    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def save_model(model):
    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_FILE,
    )

    print(
        f"\nModel saved to: {MODEL_FILE}"
    )


def load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_FILE}"
        )

    return joblib.load(
        MODEL_FILE
    )




def predict_recovery_probability(
    model,
    features: dict,
) -> float:

    dataframe = pd.DataFrame(
        [features]
    )

    probability = model.predict_proba(
        dataframe
    )[0][1]

    return float(probability)

def evaluate_model(
    model,
    X_train,
    X_test,
    y_train,
    y_test,
):
    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    return {
        "accuracy": accuracy_score(
            y_test,
            predictions,
        ),
        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "roc_auc": roc_auc_score(
            y_test,
            probabilities,
        ),
    }