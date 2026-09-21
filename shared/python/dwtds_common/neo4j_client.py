"""Async Neo4j client with parameterized Cypher only and retry.

RULE: Every Cypher statement MUST use named parameters ($param).
      F-string Cypher injection is forbidden and will raise ValueError.
"""

import asyncio

from neo4j import AsyncGraphDatabase

from .logging import get_logger

log = get_logger("neo4j")


class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None

    async def start(self):
        self._driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password),
            max_connection_pool_size=50,
            connection_timeout=15,
        )
        await self._driver.verify_connectivity()
        log.info("neo4j.connected", uri=self.uri)

    async def stop(self):
        if self._driver:
            await self._driver.close()
            log.info("neo4j.closed")

    async def run(self, cypher: str, **params) -> list[dict]:
        """Execute a parameterized Cypher query. Raises ValueError if params
        are provided but no '$' appears in the query (injection guard)."""
        if params and "$" not in cypher:
            raise ValueError(
                "Cypher query with parameters must use named params ($name). "
                "F-string Cypher is forbidden."
            )
        for attempt in range(3):
            try:
                async with self._driver.session() as session:
                    result = await session.run(cypher, **params)
                    return [dict(r) for r in await result.data()]
            except Exception as e:
                wait = min(8, 2 ** attempt)
                log.warning("neo4j.retry", attempt=attempt, error=str(e))
                await asyncio.sleep(wait)
        raise RuntimeError(f"neo4j.run failed after 3 attempts: {cypher[:80]}")

    async def run_write(self, cypher: str, **params) -> None:
        """Execute a write Cypher statement (MERGE/CREATE/SET)."""
        await self.run(cypher, **params)
