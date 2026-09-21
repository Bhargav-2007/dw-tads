"""Abstract BaseService for all 78 DW-TADS microservices.

Constructor accepts optional infrastructure clients so services can be
instantiated without live infra (e.g., in integration tests).
"""

import asyncio
import json
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from .logging import get_logger, set_correlation_id, get_correlation_id


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BaseService(ABC):
    """Standard base class for all 78 DW-TADS microservices."""

    NAME: str = "base-service"
    PLANE: int = 1
    TIER: str = "Foundation"
    INPUT_TOPICS: list[str] = []
    OUTPUT_TOPICS: list[str] = []
    HTTP_PORT: int = 0
    HTTP_ROUTES: list[str] = ["/health", "/ready", "/metrics"]

    def __init__(self, kafka=None, pg=None, neo4j=None, minio=None):
        self.kafka = kafka
        self.pg = pg
        self.neo4j = neo4j
        self.minio = minio
        self.log = get_logger(self.NAME)
        self._running = False
        self._consumer = None
        self._consumer_task: asyncio.Task | None = None
        self._seen_hashes: set[str] = set()
        self.metrics_count: int = 0

    # ------------------------------------------------------------------ #
    #  Core API                                                            #
    # ------------------------------------------------------------------ #

    @abstractmethod
    async def handle(self, message: dict) -> list[dict]:
        """Transform one input message into 0+ output messages.
        Every concrete implementation MUST read from message[...].
        """
        ...

    async def health(self) -> dict:
        return {"status": "ok", "service": self.NAME, "plane": self.PLANE}

    async def ready(self) -> dict:
        return {"status": "ready", "service": self.NAME, "plane": self.PLANE}

    # ------------------------------------------------------------------ #
    #  Lifecycle                                                           #
    # ------------------------------------------------------------------ #

    async def start(self) -> None:
        self._running = True
        self.log.info("service.start", plane=self.PLANE, tier=self.TIER)
        if self.INPUT_TOPICS and self.kafka is not None:
            self._consumer_task = asyncio.create_task(self._consumer_loop())

    async def stop(self) -> None:
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        self.log.info("service.stop")

    # ------------------------------------------------------------------ #
    #  Message Publishing                                                  #
    # ------------------------------------------------------------------ #

    async def publish(self, topic: str, payload: dict) -> None:
        """Publish a message to a Kafka topic via the injected KafkaProducer."""
        payload.setdefault("correlation_id", get_correlation_id())
        payload.setdefault("produced_by", self.NAME)
        payload.setdefault("timestamp", utc_now())
        if self.kafka is not None:
            try:
                await self.kafka.send(topic, payload)
            except Exception as e:
                self.log.error("publish.failed", topic=topic, error=str(e))
        else:
            self.log.debug("publish.no_kafka", topic=topic, payload=payload)

    # ------------------------------------------------------------------ #
    #  Consumer loop (graceful degradation if kafka unavailable)          #
    # ------------------------------------------------------------------ #

    async def _consumer_loop(self) -> None:
        if not self.INPUT_TOPICS or self.kafka is None:
            return

        broker = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
        group_id = f"dwtds-{self.NAME}"

        while self._running:
            try:
                from aiokafka import AIOKafkaConsumer
                import json as _json

                consumer = AIOKafkaConsumer(
                    *self.INPUT_TOPICS,
                    bootstrap_servers=broker,
                    group_id=group_id,
                    enable_auto_commit=False,
                    auto_offset_reset="earliest",
                    value_deserializer=lambda v: _json.loads(v.decode("utf-8")),
                    session_timeout_ms=30000,
                )
                await consumer.start()
                self.log.info("consumer.started", topics=self.INPUT_TOPICS)
                try:
                    async for msg in consumer:
                        if not self._running:
                            break
                        await self._process_one(consumer, msg.topic, msg.value)
                finally:
                    await consumer.stop()
            except asyncio.CancelledError:
                return
            except Exception as e:
                if self._running:
                    self.log.warning("consumer.error", error=str(e))
                    await asyncio.sleep(5)

    async def publish_dlq(self, topic: str, payload: any, error_msg: str) -> None:
        """Publish malformed payload to dead letter queue."""
        self.log.warning("publish.dlq", topic=topic, error=error_msg)
        if self.kafka is not None:
            await self.publish(f"{topic}.dlq", {"raw": payload, "error": error_msg})

    async def _process_one(self, consumer, topic: str, value: dict) -> None:
        if not isinstance(value, dict):
            self.log.warning("message.invalid_type", topic=topic)
            if hasattr(self, "publish_dlq"):
                res = self.publish_dlq(topic, value, "Payload must be a valid JSON object")
                if asyncio.iscoroutine(res):
                    await res
            commit_fn = getattr(consumer, "commit", None)
            if commit_fn:
                res = commit_fn()
                if asyncio.iscoroutine(res):
                    await res
            return

        # Idempotency: skip already-seen messages
        import hashlib, json
        msg_hash = hashlib.sha256(
            json.dumps(value, sort_keys=True).encode()
        ).hexdigest()
        if msg_hash in self._seen_hashes:
            self.log.debug("message.duplicate", topic=topic)
            await consumer.commit()
            return

        cid = value.get("correlation_id") or str(uuid.uuid4())
        set_correlation_id(cid)

        for attempt in range(5):
            try:
                outputs = await self.handle(value)
                break
            except Exception as e:
                wait = min(16, 2 ** attempt)
                self.log.warning("handle.retry", attempt=attempt + 1, error=str(e))
                await asyncio.sleep(wait)
        else:
            self.log.error("handle.failed_all_retries", topic=topic)
            await consumer.commit()
            return

        for out in outputs or []:
            for out_topic in self.OUTPUT_TOPICS:
                await self.publish(out_topic, out)

        self._seen_hashes.add(msg_hash)
        self.metrics_count += 1
        await consumer.commit()
