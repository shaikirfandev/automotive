# Payment Platform - Production-Grade Python Microservices

A production-grade payment backend platform demonstrating high concurrency, financial correctness, distributed transactions, fault tolerance, observability, security, and scalability.

## Technology Selection

### Why FastAPI?

| Criteria | FastAPI | Django REST | Flask | Litestar |
|----------|---------|-------------|-------|----------|
| Performance | ★★★★★ | ★★★ | ★★★ | ★★★★★ |
| Async I/O | Native | Limited | Plugin | Native |
| Type Safety | Pydantic v2 | Serializers | Manual | Attrs/Pydantic |
| API Docs | Auto OpenAPI | DRF Schema | Manual | Auto OpenAPI |
| Microservices | Excellent | Heavyweight | Good | Excellent |
| WebSocket | Native | Channels | Plugin | Native |
| Learning Curve | Low | Medium | Low | Low |

**Decision**: FastAPI — native async, automatic OpenAPI, Pydantic v2 validation, excellent performance with uvicorn/uvloop, first-class dependency injection.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Client (Web / Mobile)                         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     API Gateway (NGINX + FastAPI)                     │
│  • Auth • Rate Limiting • Routing • Correlation ID • Logging         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ User Service │  │ Payment Service  │  │ Wallet Service   │
│              │  │                  │  │                  │
│ • Register   │  │ • Create Payment │  │ • Balance        │
│ • Profile    │  │ • Process        │  │ • Credit/Debit   │
│ • KYC        │  │ • Refund         │  │ • Transfers      │
└──────────────┘  └────────┬─────────┘  └──────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │   Kafka / Events │
                  └────────┬─────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Notification │  │ Transaction  │  │ Fraud / Risk     │
│ Service      │  │ Service      │  │ Service          │
└──────────────┘  └──────────────┘  └──────────────────┘
```

## Quick Start

```bash
# Start all services with Docker Compose
docker-compose up -d

# Run tests
make test

# Run linting
make lint

# Run load tests
make load-test
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 8000 | Entry point, auth, routing |
| Auth Service | 8001 | Authentication, JWT, OAuth2 |
| User Service | 8002 | User management, profiles |
| Account Service | 8003 | Account management |
| Wallet Service | 8004 | Wallet operations, balance |
| Payment Service | 8005 | Payment lifecycle |
| Transaction Service | 8006 | Transaction processing |
| Ledger Service | 8007 | Double-entry ledger |
| Fraud Service | 8008 | Risk assessment |
| Notification Service | 8009 | Email, SMS, Push |
| Reconciliation Service | 8010 | Financial reconciliation |
| Merchant Service | 8011 | Merchant management |

## Key Design Decisions

1. **Database per Service** - Each service owns its data
2. **Event-Driven** - Kafka for async inter-service communication
3. **Double-Entry Ledger** - Financial correctness guaranteed
4. **Idempotency** - Every mutation is idempotent
5. **Saga Pattern** - Distributed transactions via compensation
6. **Circuit Breakers** - Prevent cascading failures
7. **CQRS where appropriate** - Separate read/write paths for high-throughput

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Start individual service
uvicorn services.payment_service.main:app --reload --port 8005
```
