# RecoveryOS final backend hardening patch

## 1. Recovery payment linkage in GET /api/recovery/cases/{id}

The original failed payment is stored as `RecoveryCase.payment_id`. A successful recovery through a Razorpay Payment Link creates a NEW Razorpay payment ID. Therefore a recovered case can legitimately have no `Payment` row matching `case.payment_id` while the recovery payment exists.

Add a `recovery_payment` field to the case-detail response. Find the latest `payment.captured` webhook whose payment entity has `notes.recovery_case_id == str(case.id)`, then resolve that payment through `Payment.razorpay_payment_id`.

Return:

```python
"recovery_payment": (
    {
        "razorpay_payment_id": recovery_payment.razorpay_payment_id,
        "razorpay_order_id": recovery_payment.razorpay_order_id,
        "amount_minor": recovery_payment.amount_minor,
        "currency": recovery_payment.currency,
        "method": recovery_payment.method,
        "status": recovery_payment.status,
        "error_code": recovery_payment.error_code,
        "error_step": recovery_payment.error_step,
        "error_reason": recovery_payment.error_reason,
        "error_source": recovery_payment.error_source,
        "error_description": recovery_payment.error_description,
        "created_at": recovery_payment.created_at,
        "updated_at": recovery_payment.updated_at,
    }
    if recovery_payment else None
),
```

Do not replace the original `payment` field. Keeping both preserves the distinction between the failed payment and the recovery payment.

## 2. Add the captured recovery payment to the audit timeline

When building `/api/recovery/cases/{id}/audit`, include a `recovery_payment_captured` event using the same webhook lookup. This makes the audit story explicitly show:

Payment failed -> case created -> ML -> policy -> recovery action -> recovery payment captured -> recovery completed.

## 3. Enforce the declared 30-minute cooldown

The current policy declares `cooldown_minutes=30`, but the executor currently enforces only case-open and maximum-attempt checks. That means the displayed cooldown is not yet a real safety boundary.

The bounded executor should check the latest `RecoveryAction.created_at` before creating a second automated action:

```python
from datetime import datetime, timezone

latest_action = (
    db.query(RecoveryAction)
    .filter(RecoveryAction.recovery_case_id == recovery_case.id)
    .order_by(RecoveryAction.created_at.desc())
    .first()
)

if latest_action is not None and recovery_case.attempts > 0 and cooldown_minutes > 0:
    elapsed_seconds = (
        datetime.now(timezone.utc) - latest_action.created_at
    ).total_seconds()
    remaining_seconds = cooldown_minutes * 60 - elapsed_seconds
    if remaining_seconds > 0:
        return ActionExecutionResult(
            status=ActionExecutionStatus.SKIPPED,
            action=action,
            external_id=None,
            payment_link_url=None,
            message=(
                f"Recovery cooldown active. "
                f"Retry after {int(remaining_seconds // 60) + 1} minutes."
            ),
        )
```

Pass `policy_decision.cooldown_minutes` from the policy gate into the executor. Keep the executor's hard ceiling of 2 attempts unchanged.

Also apply the same cooldown check in `execute_bounded_recovery` before delegation so the agent's tool result explicitly reports the block.

## 4. Do not change the recovered-case policy semantics

For a recovered case, `determine_recovery_action()` returning `eligible=False`, `NO_ACTION`, and `max_attempts=0` is correct for a *new* action. The UI should call this the **current policy state** and use `MLDecisionAudit` to display the original approved decision. Do not rewrite historical audit records.
