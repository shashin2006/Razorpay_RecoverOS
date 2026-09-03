/**
 * Formatting utilities for RecoveryOS
 */

export function formatTimestamp(dateInput) {
  if (!dateInput) return 'Not recorded';
  const date = new Date(dateInput);
  if (isNaN(date.getTime())) return String(dateInput);

  return new Intl.DateTimeFormat('en-IN', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  }).format(date);
}

export function formatRelativeTime(dateInput) {
  if (!dateInput) return 'Not recorded';
  const date = new Date(dateInput);
  if (isNaN(date.getTime())) return String(dateInput);

  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 5) return 'just now';
  if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;
  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays}d ago`;
}

export function getFailureCategoryLabel(code) {
  if (!code) return 'Not recorded';
  const map = {
    'bank_decline': 'Bank decline',
    'insufficient_funds': 'Insufficient funds',
    'card_expired': 'Card expired',
    'authentication_failed': '3DS authentication failed',
    'network_timeout': 'Network timeout',
    'gateway_error': 'Gateway error',
    'limit_exceeded': 'Card limit exceeded',
    'invalid_card': 'Invalid card details',
    'customer_dropped': 'Checkout abandoned',
    'alternate_payment_method': 'Alternate payment method',
  };
  const key = String(code).toLowerCase().trim();
  if (map[key]) return map[key];
  
  // Format snake_case or kebab-case into sentence casing
  const formatted = String(code).replace(/[_-]+/g, ' ');
  return formatted.charAt(0).toUpperCase() + formatted.slice(1);
}

export function getPolicyActionLabel(action) {
  if (!action) return 'Not recorded';
  const map = {
    'payment_link': 'Alternate payment link',
    'razorpay_create_payment_link': 'Alternate payment link',
    'retry_with_cooldown': 'Retry with cooldown',
    'smart_routing': 'Alternate gateway routing',
    'customer_notification': 'Customer notification',
    'escalate_to_support': 'Escalate to support',
    'block_recovery': 'Block recovery (High risk)',
    'none': 'None',
  };
  const key = String(action).toLowerCase().trim();
  if (map[key]) return map[key];

  const formatted = String(action).replace(/[_-]+/g, ' ');
  return formatted.charAt(0).toUpperCase() + formatted.slice(1);
}

/**
 * Normalizes case data from either a table row item, detail response ({ case, payment, policy, ... }),
 * or raw case object, ensuring consistent top-level properties and valid `id`.
 */
export function normalizeCase(raw) {
  if (!raw) return null;

  // Check if raw is already a detail wrapper containing { case: {...} }
  const innerCase = raw.case && typeof raw.case === 'object' ? raw.case : raw;
  const id = innerCase.id ?? raw.id;

  if (id === undefined || id === null) {
    return null;
  }

  const payment = raw.payment || innerCase.payment || null;
  const recoveryPayment = raw.recovery_payment || innerCase.recovery_payment || null;
  const policy = raw.policy || innerCase.policy || {};
  const ml = raw.latest_ml_prediction || raw.ml || innerCase.ml || innerCase.latest_ml_prediction || {};
  const latestAction = raw.latest_action || raw.recovery_action || innerCase.recovery_action || innerCase.latest_action || null;
  const decisionAudit = raw.decision_audit || innerCase.decision_audit || null;

  const attempts = innerCase.attempts ?? raw.attempts ?? latestAction?.attempt ?? 0;
  const maxAttempts = innerCase.max_attempts ?? raw.max_attempts ?? policy.max_attempts ?? policy.max_automated_attempts ?? 2;
  const amountAtRisk = innerCase.amount_at_risk_minor ?? innerCase.amount_at_risk ?? raw.amount_at_risk_minor ?? raw.amount_at_risk ?? 0;
  const amountRecovered = innerCase.amount_recovered_minor ?? innerCase.amount_recovered ?? raw.amount_recovered_minor ?? raw.amount_recovered ?? 0;

  const failureCategory = innerCase.failure_category || payment?.failure_reason || raw.failure_category || null;
  const paymentId = innerCase.payment_id || payment?.payment_id || payment?.id || raw.payment_id || null;

  const agentReasoning = raw.agent_reasoning || innerCase.agent_reasoning || raw.agent?.agent_reasoning || innerCase.agent?.agent_reasoning || null;
  const agentAssessment = raw.agent_assessment || innerCase.agent_assessment || raw.assessment || innerCase.assessment || raw.agent?.reasoning || innerCase.agent?.reasoning || null;

  return {
    ...innerCase,
    id: Number(id),
    case_code: innerCase.case_code || raw.case_code || `Case #${id}`,
    status: innerCase.status || raw.status || 'open',
    attempts,
    max_attempts: maxAttempts,
    amount_at_risk_minor: amountAtRisk,
    amount_recovered_minor: amountRecovered,
    failure_category: failureCategory,
    payment_id: paymentId,
    payment,
    recovery_payment: recoveryPayment,
    policy,
    ml,
    latest_ml_prediction: ml,
    latest_action: latestAction,
    recovery_action: latestAction,
    decision_audit: decisionAudit,
    agent: raw.agent || innerCase.agent || null,
    agent_reasoning: agentReasoning,
    agent_assessment: agentAssessment,
    currency: innerCase.currency || raw.currency || 'INR',
    created_at: innerCase.created_at || raw.created_at || null,
    updated_at: innerCase.updated_at || raw.updated_at || null,
    raw_source: raw,
  };
}

