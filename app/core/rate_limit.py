"""Naive in-memory fixed-window rate limiter (single-process deployments only)."""

from __future__ import annotations

import time
from collections import defaultdict

_hits: dict[tuple[str, str], list[float]] = defaultdict(list)


def is_rate_limited(bucket: str, key: str, *, max_hits: int, window_seconds: int) -> bool:
    now = time.monotonic()
    cutoff = now - window_seconds
    hits = _hits[(bucket, key)]
    hits[:] = [t for t in hits if t > cutoff]
    if len(hits) >= max_hits:
        return True
    hits.append(now)
    return False
