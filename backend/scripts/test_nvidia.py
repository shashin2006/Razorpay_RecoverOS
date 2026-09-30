from app.services.llm.client import (
    client,
    NVIDIA_MODEL,
)


def main():
    print("=" * 60)
    print("RecoveryOS NVIDIA LLM Connectivity Test")
    print("=" * 60)

    print(f"Model: {NVIDIA_MODEL}")

    response = client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concise AI assistant "
                    "for RecoveryOS."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Explain in one sentence what a "
                    "failed payment means."
                ),
            },
        ],
        temperature=0.2,
        max_tokens=100,
    )

    print()
    print("NVIDIA response:")
    print("-" * 60)
    print(
        response.choices[0]
        .message
        .content
    )

    print()
    print("=" * 60)
    print("NVIDIA connectivity test passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()