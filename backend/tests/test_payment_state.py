from app.services.payment_state import (
    is_valid_transition,
)


def test_failed_to_authorized_is_valid():
    assert is_valid_transition(
        "failed",
        "authorized",
    )


def test_failed_to_captured_is_valid():
    assert is_valid_transition(
        "failed",
        "captured",
    )


def test_authorized_to_captured_is_valid():
    assert is_valid_transition(
        "authorized",
        "captured",
    )


def test_captured_to_failed_is_invalid():
    assert not is_valid_transition(
        "captured",
        "failed",
    )


def test_captured_to_authorized_is_invalid():
    assert not is_valid_transition(
        "captured",
        "authorized",
    )


def test_same_state_is_valid():
    assert is_valid_transition(
        "failed",
        "failed",
    )