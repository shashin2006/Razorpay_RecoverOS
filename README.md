# RecoveryOS

### AI-assisted revenue recovery with deterministic financial controls

**RecoveryOS** detects failed payments, identifies revenue at risk,
predicts recovery potential, and executes a bounded recovery workflow
through **Razorpay Test Mode** --- with an NVIDIA-powered agent
providing reasoning while deterministic policy controls remain
authoritative.

> **AI reasons → Policy authorizes → Tools execute → Webhooks confirm →
> Audit records**

------------------------------------------------------------------------

## 1. The Problem

A failed payment does not always mean lost revenue.

Businesses need to answer four questions quickly:

1.  **What failed?**
2.  **Is the revenue recoverable?**
3.  **What is the safest intervention?**
4.  **Did the intervention actually recover the money?**

RecoveryOS turns those questions into one observable workflow instead of
treating payment recovery as a manual follow-up process.

------------------------------------------------------------------------

## 2. What RecoveryOS Does

RecoveryOS is designed for the **AI Revenue Recovery** problem:

-   Detect failed payments from Razorpay webhooks
-   Classify the payment failure
-   Create a recovery case for eligible revenue at risk
-   Predict recovery probability using ML
-   Use an NVIDIA-powered agent to reason about the case
-   Apply deterministic recovery policies before any financial action
-   Execute only bounded, approved recovery actions
-   Generate a real Razorpay Test Mode Payment Link
-   Confirm recovery through Razorpay payment events
-   Record the prediction, decision, action, and outcome
-   Maintain an audit trail for the entire lifecycle

The system is deliberately designed so that **AI is not the final
authority over financial execution**.

------------------------------------------------------------------------

# 3. Final Architecture

``` text
                         ┌─────────────────────────┐
                         │     Razorpay Gateway    │
                         │      Test Mode          │
                         └────────────┬────────────┘
                                      │
                                      │ Payment Webhook
                                      ▼
                         ┌─────────────────────────┐
                         │   Webhook Verification  │
                         │ Signature + Idempotency │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Payment Failure         │
                         │ Detection               │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Failure Classification  │
                         │                         │
                         │ bank decline / other   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     Recovery Case       │
                         │   Revenue at Risk       │
                         └────────────┬────────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                       ▼                             ▼
             ┌──────────────────┐          ┌────────────────────┐
             │   ML Prediction  │          │  Deterministic     │
             │                  │          │  Recovery Policy   │
             │ Recovery         │          │                    │
             │ Probability      │          │ Eligibility        │
             │ Recommendation   │          │ Allowed Action     │
             └────────┬─────────┘          │ Attempt Ceiling   │
                      │                    │ Safety Rules      │
                      │                    └─────────┬──────────┘
                      │                              │
                      └──────────────┬───────────────┘
                                     ▼
                         ┌─────────────────────────┐
                         │   NVIDIA Recovery Agent │
                         │                         │
                         │ Inspect case            │
                         │ Reason about recovery   │
                         │ Request approved tool   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      Policy Safety      │
                         │         Gate            │
                         │                         │
                         │ LLM request ≠ authority │
                         └────────────┬────────────┘
                                      │
                              Approved action
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     Action Executor     │
                         │                         │
                         │ Hard max: 2 automated  │
                         │ recovery attempts       │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Razorpay Payment Link   │
                         │     Recovery Action     │
                         └────────────┬────────────┘
                                      │
                                      │ Customer payment
                                      ▼
                         ┌─────────────────────────┐
                         │   Razorpay Payment      │
                         │   Captured / Paid       │
                         └────────────┬────────────┘
                                      │
                                      │ Webhook
                                      ▼
                         ┌─────────────────────────┐
                         │  Outcome Recording      │
                         │                         │
                         │ Recovery completed      │
                         │ Amount recovered        │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┴────────────────┐
                    ▼                                  ▼
          ┌────────────────────┐             ┌────────────────────┐
          │ ML Evaluation      │             │    Audit Trail     │
          │                    │             │                    │
          │ Prediction vs      │             │ Case               │
          │ actual outcome     │             │ Prediction         │
          │                    │             │ Policy             │
          │                    │             │ Action             │
          │                    │             │ Outcome            │
          └────────────────────┘             └────────────────────┘
```

### Core control principle

``` text
LLM
 │
 │ reasons / requests
 ▼
Recovery Tools
 │
 │ policy validation
 ▼
Deterministic Policy
 │
 │ authorized action
 ▼
Action Executor
 │
 ▼
Razorpay
```

**The LLM never directly controls the payment API.**

------------------------------------------------------------------------

# 4. End-to-End Recovery Flow

``` text
1. Customer payment fails
          ↓
2. Razorpay sends payment.failed webhook
          ↓
3. Webhook is verified and stored
          ↓
4. Payment failure is classified
          ↓
5. Recovery Case is created
          ↓
6. ML predicts recovery probability
          ↓
7. Deterministic policy evaluates eligibility
          ↓
8. NVIDIA agent inspects the case
          ↓
9. Requested action passes policy safety gate
          ↓
10. Action Executor creates Razorpay Payment Link
          ↓
11. Customer completes the recovery payment
          ↓
12. Razorpay sends payment confirmation webhook
          ↓
13. RecoveryOS marks the case recovered
          ↓
14. ML outcome is recorded
          ↓
15. Audit trail captures the complete lifecycle
```

------------------------------------------------------------------------

# 5. Why the Architecture Is Designed This Way

### AI should reason, not own the money movement

An LLM is useful for interpreting context and selecting an appropriate
tool, but financial execution requires predictable rules.

RecoveryOS therefore separates:

  Layer             Responsibility
  ----------------- ---------------------------------------
  NVIDIA Agent      Reasoning and tool requests
  ML Model          Recovery probability / recommendation
  Recovery Policy   Authoritative business rules
  Safety Gate       Validate requested action
  Action Executor   Perform approved operation
  Razorpay          Payment infrastructure
  Webhooks          Confirm external payment state
  Audit Trail       Record decisions and outcomes

This creates a clear boundary between **intelligence** and
**authority**.

------------------------------------------------------------------------

# 6. Failure Detection & Webhooks

RecoveryOS uses Razorpay webhooks as the event-driven entry point and
source of truth for payment state changes.

The webhook layer provides:

-   Raw request body handling
-   Razorpay signature verification
-   Webhook event-ID idempotency
-   Event persistence
-   Business-event processing
-   Support for payment lifecycle events
-   Recovery confirmation from captured payment events

The system does not treat creation of a Payment Link as successful
recovery.

**Recovery is completed only after the payment provider confirms the
successful payment event.**

------------------------------------------------------------------------

# 7. Failure Classification

The failure classifier converts payment failure information into a
recovery category.

Example:

``` text
Razorpay Payment
      │
      ├── error_code
      ├── error_step
      ├── error_source
      ├── error_reason
      └── error_description
              │
              ▼
      Failure Classifier
              │
              ▼
      bank_decline
```

This allows RecoveryOS to apply different recovery policies instead of
treating every failed payment identically.

------------------------------------------------------------------------

# 8. ML Recovery Prediction

The ML layer estimates whether a recovery case is likely to be
recoverable.

Example decision context:

``` text
Recovery Probability: 74.9%
Threshold:             40%
Recommendation:        Recover
Model Version:         baseline-v1
Mode:                  shadow
```

The ML model is **advisory**.

It does not directly authorize a payment action.

The system records the prediction and later records the actual recovery
outcome, enabling:

``` text
Prediction
    ↓
Recovery Attempt
    ↓
Actual Outcome
    ↓
ML Evaluation
```

This creates a path toward measuring whether recovery predictions are
actually useful.

------------------------------------------------------------------------

# 9. Deterministic Recovery Policy

The recovery policy is the authoritative layer for automated actions.

Current policy includes:

-   Case must be open
-   Unsupported failure categories receive no automated action
-   Bank-decline cases may use an alternate payment method
-   Automated recovery attempts are bounded
-   Hard automated recovery ceiling: **2 attempts**
-   Recovery actions are recorded with their reason and execution state

Example:

``` text
Failure:
bank_decline

        ↓

Policy:
eligible

        ↓

Action:
alternate_payment_method

        ↓

Maximum automated attempts:
2
```

The policy remains authoritative even if an LLM requests a different
action.

------------------------------------------------------------------------

# 10. NVIDIA Recovery Agent

RecoveryOS uses an NVIDIA NIM-powered agent for recovery reasoning.

The agent can:

### Inspect

Retrieve the recovery case context and understand:

-   Amount at risk
-   Failure category
-   Attempts
-   Policy state
-   ML prediction
-   Previous recovery actions

### Execute

Request a recovery action through bounded tools.

The agent does **not** receive unrestricted Razorpay API access.

Conceptually:

``` text
NVIDIA Agent
     │
     ├── inspect_recovery_case
     │
     └── execute_bounded_recovery
                    │
                    ▼
             Policy Safety Gate
                    │
                    ▼
             Action Executor
                    │
                    ▼
              Razorpay API
```

This prevents prompt-level reasoning from becoming unrestricted
financial execution.

------------------------------------------------------------------------

# 11. Real Razorpay Test Mode Recovery

RecoveryOS uses **Razorpay Test Mode** for the end-to-end demonstration.

The recovery action creates an actual Razorpay Test Mode Payment Link.

The flow is:

``` text
Failed Test Payment
       ↓
Recovery Case
       ↓
Policy-approved recovery
       ↓
Razorpay Payment Link
       ↓
Customer completes payment
       ↓
Payment captured
       ↓
Webhook received
       ↓
Recovery Case = recovered
```

This is intentionally different from simply changing a database status
to `recovered`.

The external payment event must confirm the recovery.

------------------------------------------------------------------------

# 12. Recovery Measurement

The system tracks:

-   Amount at risk
-   Amount recovered
-   Recovery case status
-   Number of recovery attempts
-   Recovery action
-   External Razorpay identifiers
-   ML prediction
-   ML recommendation
-   Actual recovery outcome

This makes the recovery workflow measurable across a batch rather than
presenting only an AI-generated recommendation.

------------------------------------------------------------------------

# 13. Audit Trail

Every important stage of the recovery lifecycle is recorded.

Typical lifecycle:

``` text
Payment Failed
      ↓
Recovery Case Created
      ↓
ML Prediction
      ↓
Policy Evaluated
      ↓
Recovery Action Recorded
      ↓
Payment Captured
      ↓
Recovery Completed
```

The audit trail makes it possible to answer:

-   Why was this case selected?
-   What did the ML model predict?
-   What did policy allow?
-   What action was requested?
-   What action was executed?
-   Which external payment was created?
-   Was the revenue actually recovered?

------------------------------------------------------------------------

# 14. Safety Model

RecoveryOS follows a defense-in-depth approach:

``` text
              ┌─────────────────────┐
              │     NVIDIA Agent    │
              │  Reasoning / Intent │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Deterministic Policy│
              │     Authority       │
              └──────────┬──────────┘
                         │
                  allowed action
                         ▼
              ┌─────────────────────┐
              │    Safety Gate      │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Action Executor    │
              │ Hard attempt ceiling│
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │      Razorpay       │
              └─────────────────────┘
```

Important safety properties:

-   LLM cannot directly call Razorpay
-   Policy controls allowed recovery actions
-   Unsupported actions are blocked
-   Automated recovery attempts are bounded
-   Webhook signatures are verified
-   Duplicate webhook events are handled idempotently
-   Recovery is confirmed by external payment events
-   Decisions and actions are auditable

------------------------------------------------------------------------

# 15. Database Model

RecoveryOS persists the recovery lifecycle using PostgreSQL.

### WebhookEvent

Stores incoming Razorpay webhook events.

Key information:

-   Razorpay event ID
-   Event type
-   Payload
-   Signature validity
-   Processing state
-   Received timestamp

### Payment

Stores payment state and failure information.

Key information:

-   Razorpay payment ID
-   Order ID
-   Amount
-   Currency
-   Payment method
-   Status
-   Error information

### RecoveryCase

Represents revenue at risk.

Key information:

-   Original payment ID
-   Amount at risk
-   Currency
-   Failure category
-   Status
-   Attempts
-   Amount recovered

### RecoveryAction

Stores an attempted recovery intervention.

Key information:

-   Recovery case
-   Action type
-   Status
-   Attempt number
-   Reason
-   External ID
-   Payment Link URL
-   Execution timestamp

### MLPrediction

Stores model predictions and eventual outcomes.

Key information:

-   Recovery probability
-   Threshold
-   Recommendation
-   Model version
-   Prediction mode
-   Actual recovered amount
-   Outcome recorded flag

### MLDecisionAudit

Stores the relationship between ML and deterministic policy.

Key information:

-   Policy eligibility
-   Policy action
-   ML probability
-   ML threshold
-   ML recommendation
-   Agreement

------------------------------------------------------------------------

# 16. Technology Stack

### Backend

-   Python 3.12
-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Pydantic
-   Uvicorn
-   pytest

### AI / ML

-   NVIDIA NIM
-   NVIDIA Nemotron models
-   scikit-learn
-   joblib

### Payments

-   Razorpay Test Mode
-   Razorpay Payment Links
-   Razorpay Webhooks

### Frontend

-   React
-   Vite
-   Tailwind CSS
-   Recharts
-   Framer Motion

------------------------------------------------------------------------

# 17. Repository Structure

``` text
Razorpay_RecoverOS/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   └── services/
│   │       ├── llm/
│   │       ├── action_executor.py
│   │       ├── action_audit.py
│   │       ├── event_processor.py
│   │       ├── failure_classifier.py
│   │       ├── ml_decision_service.py
│   │       ├── ml_evaluation.py
│   │       ├── ml_outcome_service.py
│   │       ├── ml_prediction_service.py
│   │       ├── recovery_case.py
│   │       ├── recovery_completion.py
│   │       ├── recovery_metrics.py
│   │       ├── recovery_orchestrator.py
│   │       ├── recovery_policy.py
│   │       ├── recovery_state.py
│   │       ├── risk_engine.py
│   │       └── payment_link.py
│   │
│   ├── tests/
│   ├── templates/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   └── ...
│   ├── package.json
│   └── .env.example
│
├── .env.example
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

# 18. Test Console

RecoveryOS includes a Test Mode checkout console for creating controlled
payment scenarios.

The console allows test data such as:

-   Amount
-   Customer name
-   Customer email
-   Customer mobile
-   Payment description

The backend creates a Razorpay Test Mode order and launches Razorpay
Checkout.

This keeps the demonstration close to the actual payment lifecycle
instead of relying on a fake payment simulator.

------------------------------------------------------------------------

# 19. Local Development

## Prerequisites

-   Python 3.12+
-   Node.js
-   PostgreSQL
-   Razorpay Test Mode account
-   NVIDIA API credentials

## Backend

``` bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

Create your backend `.env` using the provided example.

Start the API:

``` bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

``` text
http://127.0.0.1:8000
```

## Frontend

``` bash
cd frontend

npm install
npm run dev
```

The frontend will normally be available at:

``` text
http://localhost:5173
```

Set:

``` text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

------------------------------------------------------------------------

# 20. Environment Variables

Backend configuration includes credentials and configuration for:

``` text
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET
NVIDIA_API_KEY
DATABASE_URL
```

Frontend configuration:

``` text
VITE_API_BASE_URL
```

**Never commit real API keys, webhook secrets, database credentials, or
other secrets.**

------------------------------------------------------------------------

# 21. Webhook Setup

For local development, Razorpay must be able to reach a public webhook
endpoint.

Configure the webhook URL to point to the backend webhook route through
a suitable public tunnel or deployed backend.

Configure a dedicated webhook secret and enable the payment events
required by the application, including:

``` text
payment.failed
payment.authorized
payment.captured
order.paid
```

RecoveryOS validates the Razorpay webhook signature using the raw
request body and uses the Razorpay event ID for idempotency.

------------------------------------------------------------------------

# 22. Testing

Run the backend test suite:

``` bash
pytest
```

The tests cover important recovery behavior including:

-   Recovery policy decisions
-   Bounded action execution
-   Agent tool behavior
-   Policy enforcement
-   ML decision handling
-   Recovery workflow behavior
-   Safety against unauthorized agent actions

The project was validated with a passing backend test suite during
development.

------------------------------------------------------------------------

# 23. Example End-to-End Scenario

A representative RecoveryOS flow looks like:

``` text
Original payment
₹500
     │
     ▼
Payment failed
     │
     ▼
Recovery Case created
     │
     ▼
ML recovery probability
74.9%
     │
     ▼
Policy threshold
40%
     │
     ▼
Approved action
alternate_payment_method
     │
     ▼
Razorpay Payment Link
     │
     ▼
Customer completes payment
     │
     ▼
Payment captured
     │
     ▼
Webhook received
     │
     ▼
₹500 recovered
```

The important distinction is that **the recovery amount is confirmed
through the payment lifecycle**, rather than being claimed simply
because a recovery action was requested.

------------------------------------------------------------------------

# 24. Design Principles

### 1. AI is advisory, policy is authoritative

The model can recommend. Deterministic rules decide.

### 2. External systems are the source of truth

Razorpay payment events confirm payment outcomes.

### 3. Financial actions are bounded

Automated recovery has explicit stopping rules.

### 4. Every important action is auditable

Decisions, actions, and outcomes are persisted.

### 5. Recovery is outcome-driven

A generated payment link is not the same as recovered revenue.

### 6. Prefer real integrations over simulations

The primary demonstration uses Razorpay Test Mode.

------------------------------------------------------------------------

# 25. Buildathon Alignment

RecoveryOS directly addresses the revenue recovery workflow:

``` text
Detect revenue at risk
        ↓
Determine recovery potential
        ↓
Choose intervention
        ↓
Execute bounded recovery
        ↓
Confirm recovered revenue
        ↓
Measure outcome
        ↓
Maintain audit trail
```

The project focuses on the difficult part of agentic fintech systems:
**allowing AI to take useful action while keeping financial execution
deterministic, bounded, and observable.**

------------------------------------------------------------------------

# 26. What Makes RecoveryOS Different

RecoveryOS is not simply:

> "An LLM that sends a payment link."

It is a controlled recovery system where:

**ML predicts**

→ **AI reasons**

→ **Policy authorizes**

→ **Tools execute**

→ **Razorpay confirms**

→ **Audit records**

→ **ML evaluates**

That separation is the core architectural idea behind the project.

------------------------------------------------------------------------

# 27. Security & Safety Notes

This project is intended for demonstration using Razorpay Test Mode.

For production deployment, additional controls would be required,
including appropriate authentication/authorization, secret management,
database migrations, stronger operational monitoring, rate limiting,
customer communication controls, compliance review, and production-grade
observability.

No production payment credentials should be committed to this
repository.

------------------------------------------------------------------------

# 28. Project Status

**Working prototype / buildathon submission**

Implemented:

-   [x] Razorpay Test Mode integration
-   [x] Payment failure detection
-   [x] Failure classification
-   [x] Recovery cases
-   [x] ML recovery prediction
-   [x] Deterministic recovery policy
-   [x] NVIDIA recovery agent
-   [x] Policy-enforced agent tools
-   [x] Bounded recovery execution
-   [x] Razorpay Payment Link recovery
-   [x] Webhook-based recovery confirmation
-   [x] Recovery outcome recording
-   [x] ML outcome evaluation
-   [x] Recovery audit trail
-   [x] React dashboard
-   [x] Test checkout console
-   [x] Automated backend tests

------------------------------------------------------------------------

# 29. Official Resources

-   [Razorpay](https://razorpay.com/)
-   [Razorpay Documentation](https://razorpay.com/docs/)
-   [Razorpay Buildathon](https://razorpay.com/buildathon/)
-   [NVIDIA NIM](https://build.nvidia.com/)

------------------------------------------------------------------------

# 30. Author

**Shashin**

Built for the Razorpay AI Buildathon.

------------------------------------------------------------------------

## Final Message

RecoveryOS was built around one idea:

> **Don't just predict that revenue can be recovered. Build the
> controlled system that can actually recover it.**

**AI reasons. Policy authorizes. Tools execute. Webhooks confirm. Audit
records.**
