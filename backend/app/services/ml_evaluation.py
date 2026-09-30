from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sqlalchemy.orm import Session

from app.db.models import (
    MLDecisionAudit,
    MLPrediction,
)


def get_ml_evaluation(
    db: Session,
) -> dict:

    predictions = (
        db.query(MLPrediction)
        .filter(
            MLPrediction.outcome_recorded == True
        )
        .all()
    )

    total_predictions = len(predictions)

    if total_predictions == 0:
        return {
            "total_predictions": 0,
            "recovered_predictions": 0,
            "unrecovered_predictions": 0,
            "recovery_rate": 0.0,
            "total_revenue_recovered": 0,
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "roc_auc": None,
        }

    y_true = [
        1 if prediction.actual_recovered > 0 else 0
        for prediction in predictions
    ]

    y_pred = [
        1
        if prediction.recommendation
        else 0
        for prediction in predictions
    ]

    probabilities = [
        prediction.probability
        for prediction in predictions
    ]

    recovered_predictions = sum(y_true)

    unrecovered_predictions = (
        total_predictions
        - recovered_predictions
    )

    total_revenue_recovered = sum(
        prediction.actual_recovered or 0
        for prediction in predictions
    )

    recovery_rate = (
        recovered_predictions
        / total_predictions
    )

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    if len(set(y_true)) == 2:
        roc_auc = roc_auc_score(
            y_true,
            probabilities,
        )
    else:
        roc_auc = None

    return {
        "total_predictions": total_predictions,
        "recovered_predictions": recovered_predictions,
        "unrecovered_predictions": unrecovered_predictions,
        "recovery_rate": recovery_rate,
        "total_revenue_recovered": total_revenue_recovered,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
    }


def get_probability_bucket_analysis(
    db: Session,
) -> list[dict]:

    predictions = (
        db.query(MLPrediction)
        .filter(
            MLPrediction.outcome_recorded == True
        )
        .all()
    )

    buckets = [
        (0.40, 0.50),
        (0.50, 0.60),
        (0.60, 0.70),
        (0.70, 0.80),
        (0.80, 0.90),
        (0.90, 1.01),
    ]

    results = []

    for lower, upper in buckets:

        bucket_predictions = [
            prediction
            for prediction in predictions
            if lower <= prediction.probability < upper
        ]

        total = len(bucket_predictions)

        recovered = sum(
            1
            for prediction in bucket_predictions
            if prediction.actual_recovered > 0
        )

        revenue = sum(
            prediction.actual_recovered or 0
            for prediction in bucket_predictions
        )

        recovery_rate = (
            recovered / total
            if total > 0
            else 0.0
        )

        results.append(
            {
                "bucket": f"{lower:.2f}-{upper:.2f}",
                "predictions": total,
                "recovered": recovered,
                "recovery_rate": recovery_rate,
                "revenue_recovered": revenue,
            }
        )

    return results


def get_policy_ml_agreement(
    db: Session,
) -> dict:

    audits = (
        db.query(MLDecisionAudit)
        .all()
    )

    total = len(audits)

    if total == 0:
        return {
            "total_decisions": 0,
            "agreements": 0,
            "disagreements": 0,
            "agreement_rate": 0.0,
        }

    agreements = sum(
        1
        for audit in audits
        if audit.agreement
    )

    disagreements = (
        total - agreements
    )

    agreement_rate = (
        agreements / total
    )

    return {
        "total_decisions": total,
        "agreements": agreements,
        "disagreements": disagreements,
        "agreement_rate": agreement_rate,
    }