"""Session helpers — account lockout + idle/daily re-auth deadlines.

Lockout state lives in Redis (`shield:lockout:<email>`) so it survives worker
restarts and is consistent across web and API. JWT issuance + verification is
handled at the IdP (Keycloak) in production; for v1 dev we accept Keycloak's
bearer tokens via the auth dependency below.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import redis

from app.settings import get_settings


@dataclass
class LockoutState:
    locked: bool
    attempts: int
    retry_after_seconds: int


_settings = get_settings()
_redis = redis.Redis.from_url(_settings.redis_url, decode_responses=True)


def _key(email: str) -> str:
    return f"shield:lockout:{email.lower()}"


def record_failed_attempt(email: str) -> LockoutState:
    """Increment failed-attempt counter; return current state."""
    settings = get_settings()
    key = _key(email)
    pipe = _redis.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, settings.shield_account_lockout_window_seconds, nx=True)
    pipe.ttl(key)
    attempts, _, ttl = pipe.execute()
    locked = int(attempts) >= settings.shield_account_lockout_max_attempts
    return LockoutState(
        locked=locked,
        attempts=int(attempts),
        retry_after_seconds=int(ttl) if ttl and int(ttl) > 0 else settings.shield_account_lockout_window_seconds,
    )


def clear_failed_attempts(email: str) -> None:
    _redis.delete(_key(email))


def current_state(email: str) -> LockoutState:
    settings = get_settings()
    attempts_raw = _redis.get(_key(email))
    attempts = int(attempts_raw or 0)
    ttl = _redis.ttl(_key(email))
    return LockoutState(
        locked=attempts >= settings.shield_account_lockout_max_attempts,
        attempts=attempts,
        retry_after_seconds=max(int(ttl or 0), 0),
    )


def now_epoch() -> int:
    return int(time.time())
