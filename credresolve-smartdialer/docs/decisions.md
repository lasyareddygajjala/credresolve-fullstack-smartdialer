# Architecture decisions
This demonstrator uses one FastAPI process and an RLock around allocation. This makes atomic reservation understandable and testable, but it is not a distributed lock and state is not durable.
Production design: transactional database conditional UPDATE (`WHERE status='AVAILABLE'`), uniqueness constraint for active allocations, durable event inbox with unique provider event ID, outbox dispatch, leases and reconciliation after worker crashes. Pacing has no provider dependency; SafetyController clamps proposals to current free agents, queued borrowers and hard cap.
