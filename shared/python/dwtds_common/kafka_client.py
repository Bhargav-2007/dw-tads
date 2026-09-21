"""Kafka producer/consumer with retry, DLQ, and idempotency."""

import asyncio
import json

from .logging import get_logger, get_correlation_id

log = get_logger("kafka")


class KafkaProducer:
    def __init__(self, brokers: list[str], max_retries: int = 5):
        self.brokers = brokers
        self.max_retries = max_retries
        self._producer = None

    async def start(self):
        from aiokafka import AIOKafkaProducer
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.brokers,
            value_serializer=lambda v: json.dumps(v, default=str).encode(),
            compression_type="gzip",
            acks="all",
            enable_idempotence=True,
            retry_backoff_ms=500,
            request_timeout_ms=30000,
        )
        await self._producer.start()
        log.info("kafka.producer.started", brokers=self.brokers)

    async def stop(self):
        if self._producer:
            await self._producer.stop()
            log.info("kafka.producer.stopped")

    async def send(self, topic: str, message: dict) -> None:
        message.setdefault("correlation_id", get_correlation_id())
        for attempt in range(self.max_retries):
            try:
                await self._producer.send_and_wait(topic, message)
                return
            except Exception as e:
                wait = min(16, 2 ** attempt)
                log.warning("kafka.send.retry", topic=topic, attempt=attempt,
                            error=str(e), wait_s=wait)
                await asyncio.sleep(wait)
        raise RuntimeError(f"send to {topic} failed after {self.max_retries} retries")

    async def send_dlq(self, original_topic: str, raw: bytes, error: str):
        await self.send(f"dlq.{original_topic}", {
            "original_topic": original_topic,
            "raw": raw.decode("utf-8", errors="replace"),
            "error": error,
        })


class KafkaConsumer:
    def __init__(self, brokers: list[str], group_id: str, topics: list[str],
                 handler, validator=None):
        self.brokers = brokers
        self.group_id = group_id
        self.topics = topics
        self.handler = handler
        self.validator = validator
        self._consumer = None
        self._dlq: KafkaProducer | None = None

    async def start(self, dlq: KafkaProducer):
        from aiokafka import AIOKafkaConsumer
        self._dlq = dlq
        self._consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.brokers,
            group_id=self.group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            max_poll_records=100,
            session_timeout_ms=30000,
        )
        await self._consumer.start()

    async def stop(self):
        if self._consumer:
            await self._consumer.stop()

    async def run(self):
        async for msg in self._consumer:
            raw = msg.value
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, TypeError) as e:
                await self._dlq.send_dlq(msg.topic, raw if isinstance(raw, bytes) else str(raw).encode(), f"json: {e}")
                await self._consumer.commit()
                continue
            if self.validator:
                try:
                    payload = self.validator(payload)
                except Exception as e:
                    await self._dlq.send_dlq(msg.topic, raw if isinstance(raw, bytes) else str(raw).encode(), f"schema: {e}")
                    await self._consumer.commit()
                    continue
            try:
                await self.handler(payload)
                await self._consumer.commit()
            except Exception as e:
                log.exception("kafka.handler.error", topic=msg.topic)
                await self._dlq.send_dlq(msg.topic, raw if isinstance(raw, bytes) else str(raw).encode(), f"handler: {e}")
                await asyncio.sleep(2)
