# Deployment Guide

## Local Development

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Make

### Quick Start
```bash
cd payment-platform

# Start infrastructure (DB, Redis, Kafka, Monitoring)
docker-compose up -d postgres redis kafka zookeeper prometheus grafana jaeger

# Install Python dependencies
pip install -e ".[dev]"

# Run migrations (when DB is ready)
# alembic upgrade head

# Start a service locally
uvicorn services.payment_service.main:app --reload --port 8005

# Or start everything
docker-compose up -d
```

### Access Points
| Service | URL |
|---------|-----|
| API Gateway | http://localhost:8000 |
| Swagger UI (Payment) | http://localhost:8005/docs |
| Kafka UI | http://localhost:8080 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |
| Jaeger UI | http://localhost:16686 |

## Production Deployment (Kubernetes)

### Prerequisites
- Kubernetes cluster (1.28+)
- kubectl configured
- Helm 3 (optional)
- Container registry access

### Deployment Steps

1. **Create namespace**
```bash
kubectl apply -f infrastructure/kubernetes/base/namespace.yaml
```

2. **Deploy secrets**
```bash
kubectl create secret generic payment-db-credentials \
  --from-literal=url='******postgres:5432/payment_db' \
  -n payment-platform
```

3. **Deploy services**
```bash
kubectl apply -f infrastructure/kubernetes/base/
```

4. **Verify**
```bash
kubectl get pods -n payment-platform
kubectl get svc -n payment-platform
```

### Scaling
```bash
# Manual scaling
kubectl scale deployment payment-service --replicas=5 -n payment-platform

# HPA handles auto-scaling based on CPU/memory
# Configured in payment-service.yaml
```

### Rolling Update
```bash
kubectl set image deployment/payment-service \
  payment-service=payment-platform/payment-service:v2.0.0 \
  -n payment-platform

# Monitor rollout
kubectl rollout status deployment/payment-service -n payment-platform
```

### Rollback
```bash
kubectl rollout undo deployment/payment-service -n payment-platform
```

## CI/CD Pipeline

```
Developer → Git Push → GitHub Actions:
  1. Lint (ruff) → catches style issues
  2. Type Check (mypy) → catches type errors
  3. Unit Tests (pytest) → catches logic errors
  4. Security Scan (bandit) → catches vulnerabilities
  5. Build Docker Image → creates deployable artifact
  6. Push to Registry → stores artifact
  7. Deploy Staging → validate in staging environment
  8. Smoke Tests → verify deployment works
  9. Production Approval → manual gate
  10. Production Deploy → rolling update
```

## Monitoring

### Key Metrics to Watch
- `payment_requests_total` - Payment volume
- `payment_request_duration_seconds` - Latency (p50, p95, p99)
- `wallet_operations_total` - Wallet activity
- DB connection pool utilization
- Kafka consumer lag
- Error rates by service

### Alerts (configure in Grafana)
- Payment error rate > 1%
- p99 latency > 5s
- DB connection pool > 80% utilized
- Kafka consumer lag > 1000 messages
- Circuit breaker OPEN for > 5 minutes
- Pod restart count > 3 in 5 minutes
