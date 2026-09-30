/**
 * Mock data for isolated UI testing / preview when backend is not running locally.
 * Controlled STRICTLY by VITE_USE_MOCK_DATA=true (default: false).
 * 
 * Notice: All money values are in minor currency units (paise for INR).
 * 50000 minor units = ₹500.00
 */

export const isMockEnabled = import.meta.env.VITE_USE_MOCK_DATA === 'true';

export const mockRecoveryMetrics = {
  total_cases: 42,
  total_amount_at_risk_minor: 4850000, // ₹48,500.00
  total_amount_recovered_minor: 2182500, // ₹21,825.00
  recovered_cases: 19,
  recovery_rate: 0.452,
  amount_recovery_rate: 0.450,
  total_attempts: 31,
  executed_actions: 24,
  failed_actions: 2,
  policy_eligible_cases: 28,
  ml_predictions: 42,
  ml_outcomes_recorded: 21,
  ml_policy_agreement_rate: 0.881,
};

export const mockMLEvaluation = {
  model_name: "recoveryos-gradient-boost-v2.1",
  model_version: "2.1.4",
  last_evaluated: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
  accuracy: 0.874,
  precision: 0.891,
  recall: 0.835,
  f1_score: 0.862,
  roc_auc: 0.918,
  brier_score: 0.082,
  samples_evaluated: 1240,
  features_importance: [
    { feature: "customer_payment_history_success_rate", importance: 0.34 },
    { feature: "failure_category_historical_recoverability", importance: 0.28 },
    { feature: "amount_at_risk_normalized", importance: 0.16 },
    { feature: "time_since_failure_seconds", importance: 0.12 },
    { feature: "issuer_bank_health_score", importance: 0.10 }
  ]
};

export const mockProbabilityBuckets = [
  { bucket: "0.0 - 0.2", count: 8, label: "Very Low (<20%)", recovered_count: 0, conversion_rate: 0.0 },
  { bucket: "0.2 - 0.4", count: 6, label: "Low (20-40%)", recovered_count: 1, conversion_rate: 0.166 },
  { bucket: "0.4 - 0.6", count: 9, label: "Moderate (40-60%)", recovered_count: 4, conversion_rate: 0.444 },
  { bucket: "0.6 - 0.8", count: 12, label: "High (60-80%)", recovered_count: 8, conversion_rate: 0.666 },
  { bucket: "0.8 - 1.0", count: 7, label: "Very High (>80%)", recovered_count: 6, conversion_rate: 0.857 }
];

export const mockDecisionAgreement = {
  total_decisions: 42,
  agreement_count: 37,
  agreement_rate: 0.881,
  breakdown: {
    both_allow: 26,
    both_block: 11,
    policy_allow_ml_hesitant: 3,
    policy_block_ml_recommend: 2
  },
  policy_override_rate: 0.119,
  safety_interventions: 2
};

export const mockRecoveryCases = [
  {
    id: "rc_901a4e21",
    case_code: "RC-1042",
    amount_at_risk_minor: 500000, // ₹5,000.00
    failure_category: "bank_decline",
    failure_reason: "Issuer bank temporary transaction limit exceeded",
    gateway: "Razorpay (Test Mode)",
    customer_identifier: "cust_92j4...3k1",
    created_at: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
    status: "recovered", // recovered, awaiting_payment, processing, blocked, max_attempts_reached
    attempts: 1,
    max_attempts: 2,
    policy: {
      eligible: true,
      decision: "Policy Approved",
      recommended_action: "payment_link",
      reason: "Transient bank limit with strong customer credit track record.",
      cooldown_period_minutes: 15,
      max_automated_attempts: 2,
    },
    ml: {
      recovery_probability: 0.78,
      recommendation: "Generate Alternate Payment Link (UPI / NetBanking)",
      confidence: "High",
      model_version: "v2.1.4",
      outcome_recorded: true,
      actual_recovered: true,
    },
    agent: {
      status: "action_executed",
      agent_provider: "Recovery AI Agent",
      requested_tool: "razorpay_create_payment_link",
      agent_reasoning: "Customer has 94% lifetime checkout reliability. Bank decline is transient code 05. Generating instant UPI payment link with 24h validity.",
    },
    execution: {
      payment_link_id: "plink_test_904kL8s1",
      payment_link_url: "https://rzp.io/i/test_904kL8s1",
      status: "paid",
      recovered_amount_minor: 500000,
      completed_at: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    },
    timeline: [
      { timestamp: new Date(Date.now() - 1000 * 60 * 18).toISOString(), event: "payment_failed", title: "Payment Failure Detected", description: "Razorpay webhook received: payment.failed (bank_decline)", status: "warning" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 17).toISOString(), event: "case_created", title: "Recovery Case Initialized", description: "Case RC-1042 opened. Amount at risk: ₹5,000", status: "neutral" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 16).toISOString(), event: "policy_evaluated", title: "Deterministic Policy Evaluated", description: "Safety rule check passed: 0/2 attempts utilized. Recovery eligible.", status: "success" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), event: "ml_inferred", title: "ML Advisory Generated", description: "Scored recovery probability: 78% (High confidence)", status: "neutral" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 14).toISOString(), event: "agent_invoked", title: "Recovery Agent Inspected Case", description: "Agent requested bounded action: razorpay_create_payment_link", status: "neutral" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 13).toISOString(), event: "safety_passed", title: "Policy Safety Gate Passed", description: "Action verified against policy ceiling (attempt 1 of 2). Authorized.", status: "success" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 12).toISOString(), event: "link_created", title: "Razorpay Payment Link Created", description: "Payment link plink_test_904kL8s1 created in Test Mode.", status: "neutral" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(), event: "customer_paid", title: "Customer Payment Completed", description: "Razorpay webhook payment.captured received: ₹5,000", status: "success" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 7).toISOString(), event: "outcome_recorded", title: "Recovery Outcome Recorded", description: "Recovery verified and fed back to ML evaluation pipeline.", status: "success" }
    ]
  },
  {
    id: "rc_882c1b99",
    case_code: "RC-1043",
    amount_at_risk_minor: 1200000, // ₹12,000.00
    failure_category: "authentication_failed",
    failure_reason: "3DS OTP step timeout on mobile browser",
    gateway: "Razorpay (Test Mode)",
    customer_identifier: "cust_43m8...9p2",
    created_at: new Date(Date.now() - 1000 * 60 * 42).toISOString(),
    status: "awaiting_payment",
    attempts: 1,
    max_attempts: 2,
    policy: {
      eligible: true,
      decision: "Policy Approved",
      recommended_action: "payment_link",
      reason: "High intent transaction; 3DS authentication failure was device session timeout.",
      cooldown_period_minutes: 10,
      max_automated_attempts: 2,
    },
    ml: {
      recovery_probability: 0.82,
      recommendation: "Send Seamless UPI Recovery Link",
      confidence: "Very High",
      model_version: "v2.1.4",
      outcome_recorded: false,
      actual_recovered: null,
    },
    agent: {
      status: "action_executed",
      agent_provider: "Recovery AI Agent",
      requested_tool: "razorpay_create_payment_link",
      agent_reasoning: "Customer attempted high-value cart checkout. Requesting payment link with instant WhatsApp / SMS delivery.",
    },
    execution: {
      payment_link_id: "plink_test_882dM9v4",
      payment_link_url: "https://rzp.io/i/test_882dM9v4",
      status: "issued",
      recovered_amount_minor: 0,
      completed_at: null,
    },
    timeline: [
      { timestamp: new Date(Date.now() - 1000 * 60 * 42).toISOString(), event: "payment_failed", title: "Payment Failure Detected", description: "Razorpay webhook received: payment.failed (authentication_failed)", status: "warning" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 41).toISOString(), event: "case_created", title: "Recovery Case Initialized", description: "Case RC-1043 opened. Amount at risk: ₹12,000", status: "neutral" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 40).toISOString(), event: "policy_evaluated", title: "Deterministic Policy Evaluated", description: "Safety rule check passed: 0/2 attempts utilized. Recovery eligible.", status: "success" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 39).toISOString(), event: "agent_invoked", title: "Recovery Agent Inspected Case", description: "Agent requested bounded action: razorpay_create_payment_link", status: "neutral" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 38).toISOString(), event: "link_created", title: "Razorpay Payment Link Created", description: "Payment link plink_test_882dM9v4 issued. Awaiting customer payment.", status: "warning" }
    ]
  },
  {
    id: "rc_771f8a44",
    case_code: "RC-1044",
    amount_at_risk_minor: 1850000, // ₹18,500.00
    failure_category: "invalid_card",
    failure_reason: "Card expired / invalid CVV consecutive retries",
    gateway: "Razorpay (Test Mode)",
    customer_identifier: "cust_11x9...4w7",
    created_at: new Date(Date.now() - 1000 * 60 * 95).toISOString(),
    status: "blocked",
    attempts: 2,
    max_attempts: 2,
    policy: {
      eligible: false,
      decision: "Policy Blocked",
      recommended_action: "escalate_to_support",
      reason: "Maximum automated attempts (2/2) reached. Escalated to prevent customer friction.",
      cooldown_period_minutes: 0,
      max_automated_attempts: 2,
    },
    ml: {
      recovery_probability: 0.18,
      recommendation: "Do Not Auto-Retry; Escalate to Manual Support",
      confidence: "High",
      model_version: "v2.1.4",
      outcome_recorded: true,
      actual_recovered: false,
    },
    agent: {
      status: "policy_blocked",
      agent_provider: "Recovery AI Agent",
      requested_tool: "support_ticket_escalation",
      agent_reasoning: "Multiple card errors detected. Ceasing automated retries per deterministic policy limits.",
    },
    execution: {
      payment_link_id: null,
      payment_link_url: null,
      status: "blocked_by_policy",
      recovered_amount_minor: 0,
      completed_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    },
    timeline: [
      { timestamp: new Date(Date.now() - 1000 * 60 * 95).toISOString(), event: "payment_failed", title: "Payment Failure Detected", description: "Razorpay webhook received: payment.failed (invalid_card)", status: "error" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 94).toISOString(), event: "policy_blocked", title: "Deterministic Policy Enforced", description: "Case exceeds safe retry limit. Automated recovery blocked.", status: "error" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(), event: "escalated", title: "Escalated to Manual Support", description: "Support ticket generated for human account manager.", status: "neutral" }
    ]
  },
  {
    id: "rc_660e5d12",
    case_code: "RC-1045",
    amount_at_risk_minor: 350000, // ₹3,500.00
    failure_category: "network_timeout",
    failure_reason: "Gateway communication timeout during settlement",
    gateway: "Razorpay (Test Mode)",
    customer_identifier: "cust_77k2...1m9",
    created_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    status: "recovered",
    attempts: 1,
    max_attempts: 2,
    policy: {
      eligible: true,
      decision: "Policy Approved",
      recommended_action: "payment_link",
      reason: "Network level transient fault with zero customer fault.",
      cooldown_period_minutes: 5,
      max_automated_attempts: 2,
    },
    ml: {
      recovery_probability: 0.89,
      recommendation: "Immediate Payment Link via SMS/Email",
      confidence: "Very High",
      model_version: "v2.1.4",
      outcome_recorded: true,
      actual_recovered: true,
    },
    agent: {
      status: "action_executed",
      agent_provider: "Recovery AI Agent",
      requested_tool: "razorpay_create_payment_link",
      agent_reasoning: "Transient network timeout. Re-engaged customer with 1-click Razorpay payment link.",
    },
    execution: {
      payment_link_id: "plink_test_660nB2z9",
      payment_link_url: "https://rzp.io/i/test_660nB2z9",
      status: "paid",
      recovered_amount_minor: 350000,
      completed_at: new Date(Date.now() - 1000 * 60 * 110).toISOString(),
    },
    timeline: [
      { timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(), event: "payment_failed", title: "Payment Failure Detected", description: "Razorpay webhook received: payment.failed (network_timeout)", status: "warning" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 118).toISOString(), event: "policy_evaluated", title: "Deterministic Policy Evaluated", description: "Approved for automated link generation (attempt 1/2).", status: "success" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 110).toISOString(), event: "customer_paid", title: "Customer Paid Full Amount", description: "Payment captured via UPI. Case marked Recovered.", status: "success" }
    ]
  },
  {
    id: "rc_559a2c31",
    case_code: "RC-1046",
    amount_at_risk_minor: 950000, // ₹9,500.00
    failure_category: "insufficient_funds",
    failure_reason: "Account balance insufficient for immediate debit",
    gateway: "Razorpay (Test Mode)",
    customer_identifier: "cust_55t4...8h3",
    created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    status: "eligible", // Ready for agent execution
    attempts: 0,
    max_attempts: 2,
    policy: {
      eligible: true,
      decision: "Policy Approved",
      recommended_action: "payment_link",
      reason: "First attempt allowed. Policy permits alternate payment link with 48-hour expiration.",
      cooldown_period_minutes: 30,
      max_automated_attempts: 2,
    },
    ml: {
      recovery_probability: 0.64,
      recommendation: "Offer Split Payment / Extended Payment Link Window",
      confidence: "Moderate",
      model_version: "v2.1.4",
      outcome_recorded: false,
      actual_recovered: null,
    },
    agent: {
      status: "pending_invocation",
      agent_provider: "Recovery AI Agent",
      requested_tool: null,
      agent_reasoning: "Awaiting operator trigger or scheduled orchestrator dispatch.",
    },
    execution: {
      payment_link_id: null,
      payment_link_url: null,
      status: "not_started",
      recovered_amount_minor: 0,
      completed_at: null,
    },
    timeline: [
      { timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), event: "payment_failed", title: "Payment Failure Detected", description: "Razorpay webhook received: payment.failed (insufficient_funds)", status: "warning" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 4).toISOString(), event: "case_created", title: "Recovery Case Initialized", description: "Case RC-1046 opened. Amount at risk: ₹9,500", status: "neutral" },
      { timestamp: new Date(Date.now() - 1000 * 60 * 3).toISOString(), event: "policy_evaluated", title: "Deterministic Policy Evaluated", description: "Eligible for Recovery. 0/2 attempts used.", status: "success" }
    ]
  }
];
