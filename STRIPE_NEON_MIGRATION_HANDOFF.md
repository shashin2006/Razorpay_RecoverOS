# RecoverOS — Stripe + Neon Migration Handoff

> **Purpose:** This document is the handoff guide for the `neon-postgresql-stripe-migration` branch of RecoverOS.
>
> It is written for a new developer who needs to clone the repository, configure Neon PostgreSQL and Stripe Test Mode, run the application locally, test the failed-payment → recovery workflow, and understand the important implementation points.

---

## 1. What This Branch Contains

This branch migrates the original RecoverOS payment/database integration to:

- **Stripe Test Mode** for payment processing and recovery Checkout
- **Neon PostgreSQL** for the application database
- **Stripe CLI** for local webhook forwarding
- Existing RecoverOS recovery, ML, policy, agent, audit, and frontend logic

The migration intentionally keeps the RecoverOS core architecture intact.

### Core flow

```text
Stripe Test Mode
      ↓
/api/webhooks/stripe
      ↓
Event Processor
      ↓
Failure Classifier
      ↓
Recovery Case
      ↓
ML Prediction + Recovery Policy
      ↓
NVIDIA Recovery Agent
      ↓
Safety Gate
      ↓
Action Executor
      ↓
Stripe Checkout Session
      ↓
Customer completes test payment
      ↓
checkout.session.completed
      ↓
Recovery completed + audit + ML outcome
```

### Important principle

**Stripe is the payment provider adapter. RecoverOS remains the recovery engine.**

The LLM/agent does not receive unrestricted Stripe access. Deterministic policy remains authoritative over financial actions.

---

# 2. Branch

Use this branch:

```text
neon-postgresql-stripe-migration
```

Do **not** make migration work directly on `main`.

Clone:

```powershell
git clone https://github.com/shashin2006/Razorpay_RecoverOS.git
cd Razorpay_RecoverOS
git checkout neon-postgresql-stripe-migration
```

Verify:

```powershell
git branch --show-current
```

Expected:

```text
neon-postgresql-stripe-migration
```

---

# 3. Prerequisites

Install the following before running the project.

## Required

- Git
- Python 3.12+
- Node.js 20+
- npm
- A Neon PostgreSQL database
- A Stripe account with Test Mode enabled
- Stripe CLI
- NVIDIA API key if the AI agent functionality is being tested

## Optional

- VS Code
- PostgreSQL client / pgAdmin
- GitHub CLI

---

# 4. Repository Structure

Important directories:

```text
Razorpay_RecoverOS/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── recovery.py
│   │   │   ├── webhooks.py
│   │   │   └── ...
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── services/
│   │   │   ├── event_processor.py
│   │   │   ├── failure_classifier.py
│   │   │   ├── payment_link.py
│   │   │   ├── payment_normalizer.py
│   │   │   ├── recovery_orchestrator.py
│   │   │   ├── action_executor.py
│   │   │   └── llm/
│   │   ├── main.py
│   │   └── ...
│   ├── templates/
│   │   └── test_checkout.html
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env.example
│
├── .env.example
└── README.md
```

---

# 5. Neon PostgreSQL Setup

Create a PostgreSQL project/database in Neon.

Copy the PostgreSQL connection string provided by Neon.

The application expects SQLAlchemy + psycopg:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

Example format only:

```text
DATABASE_URL=postgresql+psycopg://myuser:mypassword@ep-example.us-east-2.aws.neon.tech/recoveryos?sslmode=require
```

**Do not commit the real connection string.**

The backend currently initializes the database schema using:

```python
Base.metadata.create_all(bind=engine)
```

This means a fresh Neon database can be initialized automatically when the backend starts.

Alembic migrations are not the primary setup mechanism for this branch yet.

---

# 6. Stripe Test Mode Setup

Log in to Stripe and make sure **Test Mode** is enabled.

You need a Stripe secret key.

Typical key format:

```text
sk_test_...
```

The application configuration also supports the publishable key:

```text
pk_test_...
```

The backend primarily requires the secret key for Stripe API operations.

---

# 7. Environment Variables

Create:

```text
backend/.env
```

using:

```text
backend/.env.example
```

A typical local configuration is:

```env
APP_NAME=RecoveryOS
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require

STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key

NVIDIA_API_KEY=your_nvidia_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=your_model
NVIDIA_SAFETY_MODEL=nvidia/nemotron-3.5-content-safety
```

### Local webhook secret

For this local development workflow, **do not add or require a Stripe webhook secret**.

The local webhook endpoint intentionally accepts Stripe CLI forwarded events without signature verification.

```text
Stripe CLI
   ↓
localhost:8000/api/webhooks/stripe
```

This is a development convenience only.

### Production warning

A production deployment should verify Stripe webhook signatures using Stripe's webhook signing secret.

---

# 8. Install Backend Dependencies

From the repository root:

```powershell
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

---

# 9. Start the Backend

From:

```text
backend/
```

run:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

Expected:

```json
{
  "status": "ok",
  "service": "recovery-os"
}
```

Database health:

```text
http://localhost:8000/health/db
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

# 10. Start Stripe CLI

Install and authenticate Stripe CLI.

Authenticate once:

```powershell
stripe login
```

Then start local webhook forwarding:

```powershell
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

Keep this terminal running.

Expected behavior:

```text
Stripe
  ↓
Stripe CLI
  ↓
localhost:8000/api/webhooks/stripe
```

The CLI will print a webhook signing secret. **Do not copy it into the local environment for this branch's intended local workflow.**

---

# 11. Start the Frontend

Open another terminal.

```powershell
cd frontend
npm install
npm run dev
```

Use the URL printed by Vite.

Depending on the current Vite configuration, it may be:

```text
http://localhost:3000
```

or:

```text
http://localhost:5173
```

The backend test console is independent of the React dashboard:

```text
http://localhost:8000/test-checkout
```

---

# 12. Recommended Terminal Layout

Use three terminals.

### Terminal 1 — Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 — Stripe CLI

```powershell
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

### Terminal 3 — Frontend

```powershell
cd frontend
npm run dev
```

---

# 13. End-to-End Test

Use:

```text
http://localhost:8000/test-checkout
```

Enter:

- Customer name
- Customer email
- 10-digit Indian mobile number
- Amount
- INR currency
- Description

The test console intentionally creates a **failed Stripe PaymentIntent** so that RecoverOS can demonstrate the recovery workflow.

The backend currently uses Stripe's test PaymentMethod:

```text
pm_card_chargeDeclined
```

This is intentional.

---

# 14. What Happens During the Failed Payment

The test endpoint:

```text
POST /api/test-checkout/order
```

creates a Stripe PaymentIntent.

Important configuration:

```python
automatic_payment_methods={
    "enabled": True,
    "allow_redirects": "never",
}
```

This prevents redirect-based payment methods from interfering with the controlled failure simulation.

The endpoint returns the PaymentIntent ID even when the test card is intentionally declined.

Expected response shape:

```json
{
  "ok": true,
  "payment_intent_id": "pi_...",
  "status": "failed",
  "amount": 50000,
  "currency": "INR",
  "environment": "Stripe Test Mode"
}
```

The amount is stored in the Stripe API's minor currency unit.

For INR:

```text
₹500 = 50000
```

---

# 15. Webhook Processing

Stripe generates:

```text
payment_intent.payment_failed
```

Stripe CLI forwards it to:

```text
POST /api/webhooks/stripe
```

The webhook layer:

1. Parses the Stripe event
2. Gets the Stripe event ID
3. Persists the event
4. Prevents duplicate processing
5. Sends the event to the existing event processor

The event processor then:

1. Normalizes the Stripe PaymentIntent
2. Creates/updates the Payment record
3. Classifies the failure
4. Creates a Recovery Case where eligible
5. Starts the recovery workflow

---

# 16. Recovery Workflow

The expected workflow is:

```text
payment_intent.payment_failed
        ↓
Payment
        ↓
Failure Classifier
        ↓
Recovery Case
        ↓
ML Prediction
        ↓
Recovery Policy
        ↓
NVIDIA Agent
        ↓
Safety Gate
        ↓
Action Executor
        ↓
Stripe Checkout Session
```

The recovery action creates a Stripe Checkout Session.

The customer receives/opens the Checkout URL.

---

# 17. Completing the Recovery Payment

The recovery Checkout Session is a real **Stripe Test Mode** Checkout Session.

When the customer completes it, Stripe sends:

```text
checkout.session.completed
```

to the local webhook endpoint through Stripe CLI.

RecoverOS then:

1. Finds the Recovery Case using `recovery_case_id` metadata
2. Checks whether the case was already recovered
3. Records the recovered amount
4. Marks the case as recovered
5. Records the ML outcome

### Important

Creating a Checkout Session does **not** mean recovery succeeded.

Recovery is only considered completed after Stripe confirms the payment event.

---

# 18. Stripe Test Cards

For normal Stripe Test Mode card testing:

### Successful card

```text
4242 4242 4242 4242
```

Use any future expiry date, any CVC, and any valid test billing details when Stripe Checkout asks for them.

### Generic declined card

```text
4000 0000 0000 0002
```

However, the RecoverOS test console's initial failure simulation currently uses:

```text
pm_card_chargeDeclined
```

so you normally do not need to manually enter a declined card for the first failure.

---

# 19. API Endpoints Useful for Testing

## Health

```text
GET /health
```

## Database health

```text
GET /health/db
```

## Swagger

```text
GET /docs
```

## Stripe test payment

```text
POST /api/test-checkout/order
```

## Stripe webhook

```text
POST /api/webhooks/stripe
```

## Test console

```text
GET /test-checkout
```

## Recovery APIs

See:

```text
backend/app/api/recovery.py
```

for the current recovery case/action endpoints.

---

# 20. Database Tables / Models

The important models are in:

```text
backend/app/db/models.py
```

### WebhookEvent

Stores provider webhook events.

Important provider-neutral fields include:

- `provider_event_id`
- event type
- payload
- processing state
- received timestamp

### Payment

Stores the payment state.

Important fields include:

- `provider`
- `provider_payment_id`
- `provider_order_id`
- amount
- currency
- method
- status
- failure information

### RecoveryCase

Represents revenue at risk.

### RecoveryAction

Represents an attempted recovery intervention.

### MLPrediction

Stores the recovery prediction and later outcome.

### MLDecisionAudit

Records the relationship between ML recommendation and deterministic policy.

---

# 21. Stripe Provider Mapping

Razorpay-specific identifiers were replaced with provider-neutral fields.

Examples:

```text
Razorpay payment ID
        ↓
provider_payment_id

Razorpay order ID
        ↓
provider_order_id

Razorpay event ID
        ↓
provider_event_id
```

Stripe is identified through:

```text
provider = "stripe"
```

This keeps the RecoverOS core less tightly coupled to a single payment provider.

---

# 22. Important Backend Files

### `backend/app/main.py`

Application entry point.

Also contains the controlled Stripe test-payment endpoint.

### `backend/app/api/webhooks.py`

Receives Stripe webhook events.

### `backend/app/services/event_processor.py`

Converts Stripe events into RecoverOS business events.

### `backend/app/services/payment_normalizer.py`

Maps Stripe PaymentIntent data into the internal Payment representation.

### `backend/app/services/failure_classifier.py`

Classifies payment failures.

### `backend/app/services/recovery_orchestrator.py`

Coordinates the recovery workflow.

### `backend/app/services/recovery_policy.py`

Contains deterministic recovery policy.

### `backend/app/services/action_executor.py`

Executes bounded approved recovery actions.

### `backend/app/services/payment_link.py`

Creates Stripe Checkout recovery sessions.

### `backend/app/services/llm/agent_tools.py`

Provides bounded tools to the AI recovery agent.

### `backend/app/db/models.py`

Database models.

### `backend/app/db/database.py`

SQLAlchemy engine/session configuration.

### `backend/app/core/config.py`

Environment/configuration management.

---

# 23. AI Safety Boundary

The intended authority chain is:

```text
NVIDIA Agent
      ↓
requests an action
      ↓
Deterministic Recovery Policy
      ↓
Safety Gate
      ↓
Action Executor
      ↓
Stripe
```

The agent should **not** directly call Stripe.

The policy controls:

- Whether the case is eligible
- Which action is permitted
- Maximum automated attempts
- Recovery state
- Other deterministic constraints

The current hard automated recovery ceiling is:

```text
2 attempts
```

---

# 24. Local Webhook Secret Policy

This branch intentionally uses a simplified local development workflow.

### Local

```text
Stripe CLI
    ↓
localhost
    ↓
/api/webhooks/stripe
```

No `STRIPE_WEBHOOK_SECRET` is required for the local CLI workflow.

### Production

A production deployment should use:

```text
Stripe webhook signing secret
        ↓
signature verification
        ↓
business event processing
```

Do not copy a development shortcut into production without implementing proper signature verification.

---

# 25. Running Tests

From the backend directory:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

The tests cover areas including:

- Event processing
- Payment normalization
- Duplicate webhook handling
- Recovery policy
- Recovery action execution
- Agent tool safety
- Payment link creation
- Recovery workflow behavior

If a test requires external services, check the individual test file before assuming it can run completely offline.

---

# 26. Troubleshooting

## Error: Stripe PaymentIntent requires return_url

If Stripe reports that redirect-based payment methods require a `return_url`, verify the test PaymentIntent contains:

```python
automatic_payment_methods={
    "enabled": True,
    "allow_redirects": "never",
}
```

Do **not** add `return_url` to the initial controlled failure simulation.

The recovery flow uses hosted Stripe Checkout separately.

---

## Error: Invalid automatic_payment_methods[allow_redirects]

The value must be exactly:

```text
always
```

or:

```text
never
```

For the RecoverOS initial failure test, use:

```text
never
```

---

## Error: Stripe PaymentIntent ID was not returned

Check:

1. The backend is running the latest branch code.
2. `/api/test-checkout/order` returned `payment_intent_id`.
3. The Stripe PaymentIntent was created.
4. The CardError handling in `backend/app/main.py` can extract the PaymentIntent ID.
5. Restart Uvicorn after modifying backend code.

---

## No webhook received

Check:

```powershell
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

Then trigger another test payment.

Make sure the backend is actually listening on port 8000.

---

## Database connection failed

Check:

```text
DATABASE_URL
```

It should use:

```text
postgresql+psycopg://...
```

and Neon requires:

```text
sslmode=require
```

Also test:

```text
http://localhost:8000/health/db
```

---

## NVIDIA agent errors

Check:

```text
NVIDIA_API_KEY
NVIDIA_BASE_URL
NVIDIA_MODEL
NVIDIA_SAFETY_MODEL
```

The core payment/webhook flow should be debugged separately from agent failures.

---

## Frontend cannot reach backend

Check:

```text
VITE_API_BASE_URL
```

The local backend is:

```text
http://localhost:8000
```

Also check that the backend CORS configuration allows the frontend origin being used.

---

# 27. Security Rules

Never commit:

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY` if your workflow treats it as environment-specific
- `DATABASE_URL` containing credentials
- `NVIDIA_API_KEY`
- Production webhook secrets
- Passwords
- Personal access tokens

Only commit:

- `.env.example`
- Safe placeholder values
- Documentation

If a real secret is accidentally committed, rotate it immediately.

---

# 28. Development Workflow for the Next Developer

Before changing code:

```powershell
git checkout neon-postgresql-stripe-migration
git pull origin neon-postgresql-stripe-migration
```

Create your own development branch from the migration branch if making substantial changes:

```powershell
git checkout -b feature/<your-change>
```

After testing:

```powershell
git status
git add .
git commit -m "describe the change"
git push origin feature/<your-change>
```

Do not force-push the migration branch unless there is an explicit reason.

---

# 29. What Not to Change Accidentally

When modifying this project, preserve these boundaries:

### Do not

- Replace RecoverOS with a different application architecture
- Move the project to CloudOpsAI architecture
- Replace the recovery policy with LLM-only decisions
- Treat a generated Checkout Session as successful recovery
- Remove webhook idempotency
- Remove recovery attempt limits
- Commit API credentials
- Add production webhook assumptions to local development
- Change `main` while testing the migration

### Do

- Keep Stripe-specific logic in the provider/payment integration layer
- Keep recovery logic provider-neutral where practical
- Let webhooks confirm external payment state
- Keep policy authoritative
- Keep financial actions bounded
- Record recovery outcomes
- Test the complete failure → recovery → confirmation lifecycle

---

# 30. Full Test Checklist

Use this checklist when handing over or validating the project.

## Environment

- [ ] Correct branch checked out
- [ ] Python environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Neon database created
- [ ] `DATABASE_URL` configured
- [ ] Stripe Test Mode enabled
- [ ] `STRIPE_SECRET_KEY` configured
- [ ] NVIDIA API key configured if agent testing is required

## Backend

- [ ] `/health` returns OK
- [ ] `/health/db` returns OK
- [ ] Swagger opens at `/docs`

## Stripe

- [ ] Stripe CLI authenticated
- [ ] `stripe listen` running
- [ ] Webhook forwarding points to `/api/webhooks/stripe`

## Failure flow

- [ ] Test payment created
- [ ] PaymentIntent ID returned
- [ ] Payment failure event received
- [ ] Payment persisted
- [ ] Recovery Case created
- [ ] ML prediction generated
- [ ] Policy evaluated
- [ ] Recovery action created

## Recovery flow

- [ ] Stripe Checkout Session created
- [ ] Checkout URL generated
- [ ] Test payment completed
- [ ] `checkout.session.completed` received
- [ ] Recovery Case marked recovered
- [ ] Amount recovered recorded
- [ ] ML outcome recorded
- [ ] Audit trail updated

---

# 31. Expected Final Demonstration

A successful demonstration should visibly show:

```text
1. Failed Stripe Test Payment
          ↓
2. Stripe webhook
          ↓
3. RecoverOS detects failure
          ↓
4. Recovery Case
          ↓
5. ML prediction
          ↓
6. Deterministic policy
          ↓
7. Agent reasoning
          ↓
8. Approved recovery action
          ↓
9. Stripe Checkout
          ↓
10. Customer completes Test Mode payment
          ↓
11. Stripe webhook confirmation
          ↓
12. Recovery marked completed
          ↓
13. Audit + ML outcome
```

The most important proof is **confirmed recovery through Stripe**, not simply creation of a payment link.

---

# 32. Files Changed in This Migration

The migration includes changes across the payment/database integration and supporting tests/scripts.

Important migrated areas include:

- `backend/app/core/config.py`
- `backend/app/db/models.py`
- `backend/app/db/database.py`
- `backend/app/main.py`
- `backend/app/api/webhooks.py`
- `backend/app/services/event_processor.py`
- `backend/app/services/payment_normalizer.py`
- `backend/app/services/payment_link.py`
- `backend/app/services/action_executor.py`
- `backend/app/services/recovery_orchestrator.py`
- `backend/app/services/llm/agent_tools.py`
- `backend/requirements.txt`
- `backend/.env.example`
- root `.env.example`
- frontend Stripe branding/test-console integration
- relevant backend tests and scripts

Old Razorpay-specific client/webhook files and the old Razorpay signature test were removed from this migration branch.

---

# 33. Quick Start

For an experienced developer, the minimum sequence is:

```powershell
git clone https://github.com/shashin2006/Razorpay_RecoverOS.git
cd Razorpay_RecoverOS
git checkout neon-postgresql-stripe-migration

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure backend/.env with Neon + Stripe + NVIDIA values

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Second terminal:

```powershell
stripe login
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

Third terminal:

```powershell
cd frontend
npm install
npm run dev
```

Then test:

```text
http://localhost:8000/test-checkout
```

---

# 34. Handoff Notes

This branch is intended to be the working Stripe + Neon migration branch.

The developer receiving this handoff should first:

1. Clone the repository.
2. Checkout `neon-postgresql-stripe-migration`.
3. Configure Neon.
4. Configure Stripe Test Mode.
5. Start Stripe CLI.
6. Start the backend.
7. Confirm `/health` and `/health/db`.
8. Run the failed-payment test.
9. Confirm the webhook reaches RecoverOS.
10. Confirm a Recovery Case is created.
11. Confirm a Stripe Checkout recovery session is created.
12. Complete the Test Mode recovery payment.
13. Confirm `checkout.session.completed`.
14. Confirm the Recovery Case becomes recovered.
15. Only then begin modifying the code.

---

## Final Architecture Summary

```text
                 STRIPE TEST MODE
                       │
                       ▼
              Stripe PaymentIntent
                       │
              payment_intent.payment_failed
                       │
                       ▼
             ┌─────────────────────┐
             │   RecoverOS Webhook  │
             └──────────┬──────────┘
                        ▼
               Event Processor
                        ▼
               Failure Classifier
                        ▼
                 Recovery Case
                   /       \
                  /         \
                 ▼           ▼
             ML Model     Policy
                 \         /
                  \       /
                   ▼     ▼
                 AI Agent
                     │
                Safety Gate
                     │
                Action Executor
                     │
                     ▼
              Stripe Checkout
                     │
                     ▼
               Test Payment
                     │
                     ▼
           checkout.session.completed
                     │
                     ▼
              Recovery Confirmed
                     │
              ┌──────┴──────┐
              ▼             ▼
          ML Outcome      Audit Trail
```

**AI reasons. Policy authorizes. Tools execute. Stripe confirms. Audit records.**
