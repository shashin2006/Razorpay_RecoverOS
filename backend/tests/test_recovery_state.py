from app.services.recovery_state import (
    is_valid_recovery_transition,
)


def test_open_to_action_pending():

    assert is_valid_recovery_transition(
        "open",
        "action_pending",
    )


def test_action_pending_to_awaiting_customer():

    assert is_valid_recovery_transition(
        "action_pending",
        "awaiting_customer",
    )


def test_awaiting_customer_to_recovered():

    assert is_valid_recovery_transition(
        "awaiting_customer",
        "recovered",
    )


def test_recovered_cannot_reopen():

    assert not is_valid_recovery_transition(
        "recovered",
        "open",
    )


def test_recovered_cannot_become_action_pending():

    assert not is_valid_recovery_transition(
        "recovered",
        "action_pending",
    )


def test_expired_is_terminal():

    assert not is_valid_recovery_transition(
        "expired",
        "open",
    )


def test_escalated_is_terminal():

    assert not is_valid_recovery_transition(
        "escalated",
        "open",
    )


def test_same_state_is_valid():

    assert is_valid_recovery_transition(
        "open",
        "open",
    )