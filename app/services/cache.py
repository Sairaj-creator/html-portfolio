import hashlib
import json
import time
from typing import Any, Optional

from app.core.config import settings

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None


class _InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> Optional[str]:
        now = time.time()
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at and now > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        expires_at = time.time() + ttl_seconds if ttl_seconds else 0.0
        self._store[key] = (expires_at, value)

    def flush(self) -> int:
        size = len(self._store)
        self._store.clear()
        return size


class CacheClient:
    def __init__(self) -> None:
        self._client = None
        if settings.redis_url and not settings.mock_mode and redis is not None:
            try:
                self._client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
                self._client.ping()
            except Exception:
                self._client = _InMemoryCache()
        else:
            self._client = _InMemoryCache()

    def get(self, key: str) -> Optional[str]:
        return self._client.get(key)  # type: ignore

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        return self._client.setex(key, ttl_seconds, value)  # type: ignore

    def flush(self) -> int:
        if hasattr(self._client, "flushall"):
            return int(self._client.flushall())  # type: ignore
        return self._client.flush()  # type: ignore


class CacheKeyGenerator:
    @staticmethod
    def generate_response_key(query: str, user_context: dict) -> str:
        normalized_query = query.lower().strip()
        payload = {
            "query": normalized_query,
            "user_role": user_context.get("role"),
            "schema_version": settings.schema_version,
        }
        payload_string = json.dumps(payload, sort_keys=True)
        cache_hash = hashlib.sha256(payload_string.encode()).hexdigest()
        return f"resp:{cache_hash}"

    @staticmethod
    def generate_typed_key(query_type: str, components: dict) -> str:
        payload_string = json.dumps(components, sort_keys=True)
        cache_hash = hashlib.sha256(payload_string.encode()).hexdigest()
        return f"{query_type.lower()}:{cache_hash}"
