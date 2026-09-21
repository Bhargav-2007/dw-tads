"""Tier: A — Real. Algorithms: JWT HS256 (PyJWT), Argon2id password hashing
(argon2-cffi), TOTP 2FA (pyotp), parameterized Neo4j queries for case lookup.
"""
import hashlib
import time
from datetime import datetime, timezone
import structlog
from common.base_service import BaseService

logger = structlog.get_logger()


class AnalystApi(BaseService):
    NAME = "analyst-api"
    PLANE = 6
    TIER = "Advanced"
    INPUT_TOPICS = []
    OUTPUT_TOPICS = ["audit.events"]
    HTTP_PORT = 8074
    HTTP_ROUTES = ["/health", "/ready", "/metrics", "/login", "/query"]

    async def handle(self, message: dict) -> list[dict]:
        cid = message["correlation_id"] if "correlation_id" in message else "cid-default"
        action = message.get("action") or "unknown"
        username = message.get("username") or ""
        password = message.get("password") or ""
        totp_code = message.get("totp_code") or ""
        query = message.get("query") or ""

        if action == "login":
            if not username or not password:
                return [{"event_type": "login_failed", "reason": "missing_credentials",
                         "correlation_id": cid}]

            # Fetch user from Postgres
            user_row = None
            if self.pg is not None:
                try:
                    user_row = await self.pg.fetchrow(
                        "SELECT user_id, password_hash, mfa_secret, role FROM users WHERE username=$1",
                        username
                    )
                except Exception as e:
                    logger.warning("analyst_api_pg_error", error=str(e), correlation_id=cid)

            if not user_row:
                return [{"event_type": "login_failed", "reason": "user_not_found",
                         "correlation_id": cid}]

            # Argon2 verify
            try:
                from argon2 import PasswordHasher
                ph = PasswordHasher()
                ph.verify(user_row["password_hash"], password)
                pwd_ok = True
            except Exception:
                pwd_ok = False

            if not pwd_ok:
                return [{"event_type": "login_failed", "reason": "bad_password",
                         "correlation_id": cid}]

            # TOTP verify
            if totp_code:
                try:
                    import pyotp
                    totp = pyotp.TOTP(user_row["mfa_secret"])
                    mfa_ok = totp.verify(totp_code)
                except Exception:
                    mfa_ok = False
            else:
                mfa_ok = False

            if not mfa_ok:
                return [{"event_type": "login_failed", "reason": "bad_totp", "correlation_id": cid}]

            # Issue JWT
            import jwt
            import os
            secret = os.getenv("JWT_SECRET", "dwtads-dev-secret-change-me")
            token = jwt.encode({
                "sub": str(user_row["user_id"]),
                "username": username,
                "role": user_row["role"],
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600,
            }, secret, algorithm="HS256")

            return [{"event_type": "login_success", "username": username,
                     "role": user_row["role"], "token": token,
                     "action": "LOGIN", "resource": username,
                     "actor_user": username, "correlation_id": cid}]

        elif action == "query" and query and self.neo4j is not None:
            # Parameterized read-only query
            try:
                query_hash = hashlib.sha256(query.encode()).hexdigest()
                rows = await self.neo4j.run(
                    "MATCH (n) WHERE n.id=$q OR n.value=$q RETURN n LIMIT 100",
                    q=query,
                )
                result_hash = hashlib.sha256(str(rows).encode()).hexdigest()
                return [{"event_type": "query_executed", "query_hash": query_hash,
                         "result_hash": result_hash, "result_count": len(rows),
                         "action": "QUERY", "resource": query_hash,
                         "actor_user": "api", "correlation_id": cid}]
            except Exception as e:
                return [{"event_type": "query_failed", "error": str(e), "correlation_id": cid}]

        return []
