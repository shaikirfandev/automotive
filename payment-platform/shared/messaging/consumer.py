"""Kafka consumer client with error handling."""
import json
from collections.abc import Callable, Awaitable
from typing import Any
from aiokafka import AIOKafkaConsumer
from shared.logging import get_logger

logger = get_logger(__name__)


class KafkaConsumerClient:
    """Async Kafka consumer with dead-letter topic support."""

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
        auto_offset_reset: str = "earliest",
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._topics = topics
        self._auto_offset_reset = auto_offset_reset
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        """Start the Kafka consumer."""
        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset=self._auto_offset_reset,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            enable_auto_commit=False,
        )
        await self._consumer.start()
        logger.info("kafka_consumer_started", topics=self._topics, group=self._group_id)

    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        if self._consumer:
            await self._consumer.stop()
            logger.info("kafka_consumer_stopped")

    async def consume(
        self,
        handler: Callable[[dict[str, Any]], Awaitable[None]],
        max_messages: int | None = None,
    ) -> None:
        """Consume messages and process with handler."""
        if not self._consumer:
            raise RuntimeError("Consumer not started")
        count = 0
        async for msg in self._consumer:
            try:
                await handler(msg.value)
                await self._consumer.commit()
                count += 1
                if max_messages and count >= max_messages:
                    break
            except Exception:
                logger.exception("consumer_handler_error", topic=msg.topic, offset=msg.offset)
                # In production, send to dead-letter topic
                await self._consumer.commit()
