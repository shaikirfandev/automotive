"""Load tests using Locust.

Simulates realistic payment platform traffic:
- User registration/login
- Wallet operations (credit, debit)
- Payment creation and processing
- Balance checks

Run with:
  locust -f locustfile.py --headless -u 1000 -r 50 -t 300s --host http://localhost:8000

Metrics to monitor:
- p50, p95, p99 response times
- Requests per second (RPS)
- Error rate
- Database connection pool utilization
- Kafka consumer lag
"""
from locust import HttpUser, task, between, events
import uuid
import random


class PaymentPlatformUser(HttpUser):
    """Simulates a typical payment platform user."""
    
    wait_time = between(1, 3)  # Think time between requests

    def on_start(self):
        """Called when user starts - create wallet."""
        self.user_id = str(uuid.uuid4())
        self.wallet_id = None

    @task(3)
    def check_health(self):
        """Health check - lightweight, high frequency."""
        self.client.get("/health")

    @task(5)
    def create_payment(self):
        """Create a new payment."""
        self.client.post(
            "/api/v1/payments",
            json={
                "payer_id": self.user_id,
                "payee_id": str(uuid.uuid4()),
                "amount": random.randint(100, 100000),
                "currency": "INR",
                "payment_method": "WALLET",
                "description": "Load test payment",
            },
            headers={
                "Idempotency-Key": str(uuid.uuid4()),
                "X-Request-ID": str(uuid.uuid4()),
            },
        )

    @task(3)
    def create_wallet(self):
        """Create wallet."""
        response = self.client.post(
            "/api/v1/wallets",
            json={"user_id": self.user_id, "currency": "INR"},
        )
        if response.status_code == 201:
            self.wallet_id = response.json().get("id")

    @task(4)
    def credit_wallet(self):
        """Credit wallet."""
        if self.wallet_id:
            self.client.post(
                f"/api/v1/wallets/{self.wallet_id}/credit",
                json={
                    "amount": random.randint(1000, 50000),
                    "reference_id": str(uuid.uuid4()),
                    "description": "Load test credit",
                },
            )

    @task(2)
    def get_wallet(self):
        """Check balance."""
        if self.wallet_id:
            self.client.get(f"/api/v1/wallets/{self.wallet_id}")


class HighConcurrencyPaymentUser(HttpUser):
    """Simulates concurrent payment attempts (stress test).
    
    Tests:
    - Idempotency under load
    - Race conditions
    - Connection pool exhaustion
    """
    
    wait_time = between(0.1, 0.5)  # Very aggressive timing

    def on_start(self):
        self.user_id = str(uuid.uuid4())
        self.idempotency_key = str(uuid.uuid4())

    @task
    def concurrent_payment_same_key(self):
        """Send same idempotency key rapidly - tests idempotency under load."""
        self.client.post(
            "/api/v1/payments",
            json={
                "payer_id": self.user_id,
                "payee_id": str(uuid.uuid4()),
                "amount": 5000,
                "currency": "INR",
                "payment_method": "WALLET",
            },
            headers={"Idempotency-Key": self.idempotency_key},
        )
