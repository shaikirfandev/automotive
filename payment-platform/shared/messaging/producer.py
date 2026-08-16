"""Kafka producer client with retry and serialization."""
import json
from typing import Any
from aiokafka import AIOKafkaProducer
from shared.logging import get_logger

logger = get_logger(__name__)


class KafkaProducerClient:
    """Async Kafka producer with JSON serialization."""

    def __init__(self, bootstrap_servers: str) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Start the Kafka producer."""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            enable_idempotence=True,
            max_batch_size=16384,
            linger_ms=10,
        )
        await self._producer.start()
        logger.info("kafka_producer_started")

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self._producer:
            await self._producer.stop()
            logger.info("kafka_producer_stopped")

    async def send(self, topic: str, value: dict[str, Any], key: str | None = None) -> None:
        """Send a message to a Kafka topic."""
        if not self._producer:
            raise RuntimeError("Producer not started")
        await self._producer.send_and_wait(topic, value=value, key=key)
        logger.info("kafka_message_sent", topic=topic, key=key)
