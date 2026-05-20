from __future__ import annotations

import hashlib
import time
from collections import defaultdict, deque
from collections.abc import Callable
from threading import RLock


class InMemoryRateLimiter:
    def __init__(self, time_func: Callable[[], float] | None = None) -> None:
        self._time_func = time_func or time.monotonic
        self._requests: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = RLock()

    def check(self, identity: str, limit: int, window_seconds: int = 60) -> int | None:
        if limit <= 0:
            return None

        now = self._time_func()
        window_start = now - window_seconds
        with self._lock:
            entries = self._requests[identity]
            while entries and entries[0] <= window_start:
                entries.popleft()

            if len(entries) >= limit:
                retry_after = max(1, int(window_seconds - (now - entries[0])))
                return retry_after

            entries.append(now)
            return None

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()


def rate_limit_identity(api_key: str | None, client_host: str | None) -> str:
    if api_key:
        digest = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        return f"api-key:{digest}"
    return f"ip:{client_host or 'unknown'}"
