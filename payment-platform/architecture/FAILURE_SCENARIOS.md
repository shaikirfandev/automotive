# Production Failure Scenarios & Recovery

## Overview

This document describes how the payment platform behaves under various failure conditions.
The key principle: **A successful financial transaction must NEVER be reversed due to a non-critical service failure.**

---

## Scenario 1: PostgreSQL Becomes Unavailable

### Failure
Database connections fail, queries timeout.

### Detection
- Connection pool exhaustion errors
- Health check `/readiness` fails (DB ping timeout)
- Prometheus: `db_connection_errors_total` spikes

### Protection
- Circuit breaker opens after 5 failures
- Service returns 503 Service Unavailable
- Kubernetes readiness probe fails → pod removed from service endpoints
- No traffic routed to unhealthy pods

### Recovery
- When PostgreSQL recovers, connection pool re-establishes connections (`pool_pre_ping=True`)
- Circuit breaker transitions to HALF_OPEN after recovery_timeout
- Successful requests close the circuit
- Kubernetes readiness probe succeeds → pod receives traffic again

### Data Consistency
- No data corruption (transactions were never partially committed)
- Clients retry with same idempotency key → safe
- In-flight requests that timed out: client retries, idempotency ensures no duplicate

---

## Scenario 2: Redis Becomes Unavailable

### Failure
Redis connection refused or timeout.

### Detection
- Connection errors in Redis client
- Cache operations fail
- Rate limiter falls back

### Protection
- **Cache-aside pattern**: On Redis failure, all requests go to PostgreSQL (slower but correct)
- Rate limiting degrades gracefully (in-memory fallback or skip)
- Idempotency check falls through to database UNIQUE constraint
- Service remains operational (Redis is NOT source of truth for financial data)

### Recovery
- Redis reconnects automatically
- Cache warms up gradually via cache-aside pattern
- No manual intervention required

### Data Consistency
- **Zero impact on financial data** — Redis never holds authoritative financial state
- Slightly higher DB load during outage (acceptable)

### Why Redis is NOT Source of Truth for Money
```
If Redis says balance = ₹1000 but DB says balance = ₹500:
  → DB is ALWAYS correct
  → Redis is a performance optimization only
  → Losing Redis = losing speed, not data
```

---

## Scenario 3: Kafka Becomes Unavailable

### Failure
Kafka brokers unreachable, produce/consume fails.

### Detection
- Producer send failures
- Consumer poll timeouts
- Kafka health check fails

### Protection
- **Transactional Outbox Pattern**:
  - Instead of publishing directly to Kafka, write event to `outbox` table in same DB transaction as business data
  - Background worker polls outbox → publishes to Kafka → marks as published
  - If Kafka is down, events accumulate in outbox (bounded by TTL)
- Payment processing continues (synchronous path works without Kafka)
- Notifications are delayed, not lost

### Recovery
- When Kafka recovers, outbox worker drains accumulated events
- Consumers process backlog (may cause temporary spike in notifications)
- Consumer lag metric shows processing delay

### Data Consistency
- Financial transactions are committed to PostgreSQL regardless of Kafka
- Events are guaranteed to be published eventually (at-least-once)
- Consumer idempotency prevents duplicate processing

---

## Scenario 4: Fraud Service Becomes Slow

### Failure
Fraud check response time increases from 50ms to 10+ seconds.

### Detection
- Request latency spikes on fraud check
- Circuit breaker failure count increases
- Timeout errors in payment service

### Protection
- **Timeout**: Every fraud check has a 5-second timeout
- **Circuit breaker**: After 5 timeouts, circuit opens
- **Graceful degradation**: When circuit is open:
  - Low-risk payments (< ₹5000) → approve with flag for async review
  - High-risk payments → queue for manual review
  - Never block all payments indefinitely

### Recovery
- Circuit breaker transitions to HALF_OPEN after 30s
- Test requests flow to fraud service
- If successful → circuit closes, normal operation resumes

### Data Consistency
- Payments approved without fraud check are flagged
- Async fraud review runs later (from Kafka event)
- If fraud detected post-facto → initiate refund/reversal

---

## Scenario 5: Notification Service Goes Down

### Failure
Notification service crashes or becomes unresponsive.

### Detection
- Health check fails
- Kafka consumer stops processing notification events
- Consumer lag increases

### Protection
- **Critical principle**: Payment success is NEVER dependent on notification delivery
- Payment completes → Kafka event emitted → notification service processes when available
- Dead-letter queue for repeatedly failing notifications

### Recovery
- Service restarts → consumer catches up on Kafka backlog
- Users receive delayed notifications
- DLQ handler retries permanently failed notifications

### Data Consistency
- Zero impact on financial state
- Notifications are best-effort, eventually delivered

---

## Scenario 6: Same Payment Request Arrives 10 Times Simultaneously

### Failure
Network issues cause client to retry rapidly, or intentional replay attack.

### Detection
- Idempotency key collision in database

### Protection
```
Request 1: INSERT payment (idempotency_key='ABC') → Success (201)
Request 2-10: INSERT payment (idempotency_key='ABC') → UNIQUE violation → Return cached (200)
```

- PostgreSQL UNIQUE constraint on `idempotency_key` guarantees exactly-once at DB level
- Redis cache accelerates duplicate detection (avoid DB round-trip)
- Application-level check alone is INSUFFICIENT due to race conditions

### Data Consistency
- Exactly ONE payment created
- All duplicate requests receive the same response
- No money moved multiple times

---

## Scenario 7: Two Concurrent Payments Attempt Same Balance

### Failure
User balance = ₹1000. Payment A (₹800) and Payment B (₹700) arrive simultaneously.

### Detection
- SELECT FOR UPDATE lock contention

### Protection
```sql
-- Payment A acquires lock first:
BEGIN;
SELECT balance FROM wallets WHERE id = 'X' FOR UPDATE;  -- Gets ₹1000, locks row
-- Payment B blocks here, waiting for lock

-- Payment A continues:
UPDATE wallets SET balance = 1000 - 800 = 200 WHERE id = 'X';
COMMIT;  -- Lock released

-- Payment B gets lock:
SELECT balance FROM wallets WHERE id = 'X' FOR UPDATE;  -- Gets ₹200
-- ₹200 < ₹700 → INSUFFICIENT_BALANCE → ROLLBACK
```

### Data Consistency
- Only one payment succeeds (₹800)
- Second payment correctly fails with INSUFFICIENT_BALANCE
- No negative balance possible
- No money created or destroyed

---

## Scenario 8: Kafka Consumer Crashes After Processing, Before Acknowledging

### Failure
Consumer processes event (e.g., sends notification) → crashes before committing offset.

### Detection
- Consumer group rebalance (Kafka detects member left)
- Event is re-delivered to another consumer in the group

### Protection
- **Consumer idempotency**: Each consumer checks `processed_events` table before acting
```
Event arrives (event_id = 'EVT-123'):
  1. Check: SELECT FROM processed_events WHERE event_id = 'EVT-123'
  2. If exists → skip (already processed)
  3. If not → process + INSERT into processed_events + commit offset
```
- All processing is idempotent (sending same notification twice is acceptable)

### Data Consistency
- Event is processed exactly-once (effectively-once semantics)
- No duplicate financial operations
- At worst: duplicate notification (acceptable)

---

## Scenario 9: Payment Succeeds but Client Never Receives Response

### Failure
Network drops after server commits but before response reaches client.

### Detection
- Client timeout → client retries

### Protection
- Client retries with **same idempotency key**
- Server detects duplicate → returns cached successful response
- Client receives confirmation on retry

### Data Consistency
- Payment was already successful (committed to DB)
- Client retry simply fetches existing state
- No duplicate payment execution

---

## Scenario 10: Service Crashes Halfway Through a Saga

### Failure
Payment saga: Debit wallet succeeded → Service crashes → Credit never happens.

### Detection
- Saga record in DB shows state = "DEBITED" (not COMPLETED)
- Saga recovery worker polls for stale sagas (state not terminal after X minutes)

### Protection
- **Saga state persisted in DB** at each step
- **Recovery worker** (background job):
  1. Find sagas stuck in non-terminal state for > 5 minutes
  2. For each stuck saga:
     - If DEBITED but not CREDITED → execute compensation (credit payer back)
     - Mark payment REVERSED
     - Emit compensation events

### Recovery Flow
```
Saga stuck at DEBITED:
  → Recovery worker detects
  → Compensate: Credit payer (reverse the debit)
  → Update saga state: REVERSED
  → Emit PaymentReversed event
  → Alert operations team
```

### Data Consistency
- Payer's money is returned (no money lost)
- Transaction marked as REVERSED (audit trail complete)
- Ledger entries: debit + compensating credit (balanced)
