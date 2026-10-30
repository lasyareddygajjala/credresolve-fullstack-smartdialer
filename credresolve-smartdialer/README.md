# CredResolve SmartDialer — functional prototype

A small FastAPI prototype demonstrating progressive and predictive pacing with an independent safety controller, agent/borrower reservation, explicit call states, provider abstraction and duplicate/out-of-order event handling.

## Run locally

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. `POST /dial` supports `progressive` or `predictive` and provider `provider_a` / `provider_b`; `GET /state` shows state; `POST /events` applies provider events. Run `pytest -q` for tests.

## Design

`PredictivePacingEngine` only proposes a number. `SafetyController` independently caps it against available agents, queued borrowers and a hard cap. `Dialer` allocates under a re-entrant in-process lock and reserves the agent and borrower before calling the provider. Provider A is fast/reliable; Provider B simulates timeouts, duplicate callbacks and out-of-order callbacks. Event IDs are idempotent and the transition table rejects illegal transitions.

## Production gaps (explicit)

This prototype's lock and memory store protect only one process. Production must use atomic database transactions/conditional updates or a distributed lease for agent + borrower reservation; durable event inbox with unique provider-event key; transactional outbox; idempotency keys at provider boundary; lease expiry/reconciliation after worker crash; provider circuit breaker; metrics/alerts; and a persistent audit log. The prototype intentionally does not claim multi-worker safety.
