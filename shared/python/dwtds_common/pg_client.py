"""Async Postgres client with advisory-lock-protected audit chain.

Every write to audit_log acquires Postgres advisory lock 42 before
computing the hash chain link, ensuring append-only integrity.
"""

import hashlib
import json

import asyncpg

from .logging import get_logger

log = get_logger("postgres")
AUDIT_LOCK_ID = 42


class PgClient:
    def __init__(self, dsn: str, min_pool: int = 2, max_pool: int = 10):
        self.dsn = dsn
        self.min_pool = min_pool
        self.max_pool = max_pool
        self._pool: asyncpg.Pool | None = None

    async def start(self):
        self._pool = await asyncpg.create_pool(
            self.dsn, min_size=self.min_pool, max_size=self.max_pool,
            command_timeout=30,
        )
        log.info("postgres.pool.started", dsn=self.dsn[:30] + "…")

    async def stop(self):
        if self._pool:
            await self._pool.close()
            log.info("postgres.pool.stopped")

    async def fetch(self, query: str, *args) -> list:
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args) -> str:
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def write_audit(
        self,
        event_type: str,
        actor_user: str,
        action: str,
        resource: str = "",
        query_hash: str = "",
        result_hash: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Write one audit log row with advisory-lock protected hash chain.

        Acquires pg_advisory_xact_lock(42), reads the previous hash, computes
        this_hash = sha256(prev+event_type+actor+action+resource+query+result),
        inserts the row, releases the lock.
        Returns this_hash.
        """
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "SELECT pg_advisory_xact_lock($1)", AUDIT_LOCK_ID
                )
                prev_row = await conn.fetchrow(
                    "SELECT this_hash FROM audit_log ORDER BY audit_id DESC LIMIT 1"
                )
                prev = prev_row["this_hash"] if prev_row else "0" * 64
                payload_str = (
                    f"{prev}{event_type}{actor_user}{action}"
                    f"{resource}{query_hash}{result_hash}"
                )
                this_hash = hashlib.sha256(payload_str.encode()).hexdigest()
                await conn.execute(
                    """
                    INSERT INTO audit_log(
                        event_type, actor_user, action, resource,
                        query_hash, result_hash, prev_hash, this_hash, metadata
                    ) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)
                    """,
                    event_type,
                    actor_user,
                    action,
                    resource,
                    query_hash,
                    result_hash,
                    prev,
                    this_hash,
                    json.dumps(metadata or {}),
                )
                return this_hash

    async def write_source_fetch(
        self,
        source_name: str,
        url: str,
        record_count: int = 0,
        http_status: int | None = None,
        duration_ms: int | None = None,
        cache_hit: bool = False,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Persist a source_fetches row for observability."""
        await self.execute(
            """
            INSERT INTO source_fetches(
                source_name, url, record_count, http_status,
                duration_ms, cache_hit, success, error
            ) VALUES($1,$2,$3,$4,$5,$6,$7,$8)
            """,
            source_name,
            url,
            record_count,
            http_status,
            duration_ms,
            cache_hit,
            success,
            error,
        )
