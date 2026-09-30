import csv
import random
from pathlib import Path


OUTPUT_FILE = Path(
    "data/recovery_dataset_synthetic.csv"
)

NUM_SAMPLES = 5000

PAYMENT_METHODS = [
    "netbanking",
    "upi",
    "card",
    "wallet",
]

CURRENCIES = [
    "INR",
]

FAILURE_PROFILES = [
    {
        "category": "bank_decline",
        "error_source": "bank",
        "error_step": "payment_authorization",
        "error_reason": "payment_failed",
        "error_code": "BAD_REQUEST_ERROR",
        "base_probability": 0.45,
    },
    {
        "category": "customer_action_required",
        "error_source": "customer",
        "error_step": "payment_authorization",
        "error_reason": "action_required",
        "error_code": "BAD_REQUEST_ERROR",
        "base_probability": 0.60,
    },
    {
        "category": "payment_processing_error",
        "error_source": "gateway",
        "error_step": "payment_processing",
        "error_reason": "processing_error",
        "error_code": "GATEWAY_ERROR",
        "base_probability": 0.25,
    },
    {
        "category": "unknown",
        "error_source": "unknown",
        "error_step": "unknown",
        "error_reason": "unknown",
        "error_code": "UNKNOWN_ERROR",
        "base_probability": 0.15,
    },
]


def choose_failure_profile():
    return random.choice(FAILURE_PROFILES)


def calculate_recovery_probability(
    base_probability,
    amount_minor,
    payment_method,
):
    probability = base_probability

    # Smaller payments are slightly easier to recover.
    if amount_minor <= 50000:
        probability += 0.05
    elif amount_minor >= 200000:
        probability -= 0.08

    # Payment-method variation.
    if payment_method == "upi":
        probability += 0.05

    if payment_method == "wallet":
        probability -= 0.03

    return max(
        0.05,
        min(0.90, probability),
    )


def generate_row():
    amount_minor = random.choice(
        [
            10000,
            25000,
            50000,
            75000,
            100000,
            150000,
            200000,
            500000,
        ]
    )

    payment_method = random.choice(
        PAYMENT_METHODS
    )

    profile = choose_failure_profile()

    attempts = random.choice(
        [1, 1, 1, 2, 2, 3]
    )

    probability = calculate_recovery_probability(
        base_probability=profile["base_probability"],
        amount_minor=amount_minor,
        payment_method=payment_method,
    )

    # More attempts reduce the chance that another
    # attempt will recover the payment.
    probability -= (attempts - 1) * 0.08

    probability = max(
        0.05,
        min(0.90, probability),
    )

    recovered = int(
        random.random() < probability
    )

    if recovered:
        amount_recovered = amount_minor
    else:
        amount_recovered = 0

    return {
        "amount_minor": amount_minor,
        "currency": random.choice(CURRENCIES),
        "payment_method": payment_method,
        "failure_category": profile["category"],
        "error_source": profile["error_source"],
        "error_step": profile["error_step"],
        "error_reason": profile["error_reason"],
        "error_code": profile["error_code"],
        "attempts": attempts,
        "action_type": "alternate_payment_method",
        "attempt_number": attempts,
        "recovered": recovered,
        "amount_recovered": amount_recovered,
        "data_source": "synthetic",
    }


def main():
    random.seed(42)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = [
        generate_row()
        for _ in range(NUM_SAMPLES)
    ]

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

    recovered = sum(
        row["recovered"] == 1
        for row in rows
    )

    unrecovered = (
        len(rows) - recovered
    )

    print("Synthetic RecoveryOS dataset created.")
    print("File:", OUTPUT_FILE)
    print("Rows:", len(rows))
    print("Recovered:", recovered)
    print("Unrecovered:", unrecovered)

    print(
        "Recovery rate:",
        round(
            recovered / len(rows) * 100,
            2,
        ),
        "%",
    )


if __name__ == "__main__":
    main()