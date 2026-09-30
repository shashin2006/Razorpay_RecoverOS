from types import SimpleNamespace

from app.services.recovery_policy import (
    RecoveryAction,
    determine_recovery_action,
)


def make_case(
    status="open",
    failure_category="bank_decline",
    attempts=0,
):

    return SimpleNamespace(
        status=status,
        failure_category=failure_category,
        attempts=attempts,
    )


def test_bank_decline_gets_alternate_payment_action():

    case = make_case()

    decision = determine_recovery_action(case)

    assert decision.eligible is True
    assert (
        decision.action
        == RecoveryAction.ALTERNATE_PAYMENT_METHOD
    )
    assert decision.max_attempts == 2
    assert decision.cooldown_minutes == 30


def test_max_attempts_blocks_automation():

    case = make_case(attempts=2)

    decision = determine_recovery_action(case)

    assert decision.eligible is False
    assert decision.action == RecoveryAction.ESCALATE


def test_non_open_case_gets_no_action():

    case = make_case(status="recovered")

    decision = determine_recovery_action(case)

    assert decision.eligible is False
    assert decision.action == RecoveryAction.NO_ACTION


def test_unknown_failure_gets_no_action():

    case = make_case(
        failure_category="unknown",
    )

    decision = determine_recovery_action(case)

    assert decision.eligible is False
    assert decision.action == RecoveryAction.NO_ACTION