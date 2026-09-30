from app.ml.model import (
    save_model,
    train_model,
)


DATASET = (
    "data/recovery_dataset_synthetic.csv"
)


def main():

    print(
        "Training RecoveryOS baseline model..."
    )

    model, metrics = train_model(
        DATASET
    )

    save_model(model)

    print(
        "\nBaseline model training complete."
    )


if __name__ == "__main__":
    main()