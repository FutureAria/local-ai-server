from app.services.rate_limiter import InMemoryRateLimiter, rate_limit_identity


def test_rate_limiter_blocks_after_limit_until_window_expires() -> None:
    now = 1000.0
    limiter = InMemoryRateLimiter(time_func=lambda: now)

    assert limiter.check("ip:test", limit=2, window_seconds=60) is None
    assert limiter.check("ip:test", limit=2, window_seconds=60) is None
    assert limiter.check("ip:test", limit=2, window_seconds=60) == 60

    now = 1061.0
    assert limiter.check("ip:test", limit=2, window_seconds=60) is None


def test_rate_limiter_can_be_disabled() -> None:
    limiter = InMemoryRateLimiter()

    for _ in range(10):
        assert limiter.check("ip:test", limit=0) is None


def test_rate_limit_identity_hashes_api_key() -> None:
    identity = rate_limit_identity("secret", "127.0.0.1")

    assert identity.startswith("api-key:")
    assert "secret" not in identity
