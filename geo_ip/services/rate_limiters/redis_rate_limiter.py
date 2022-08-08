"""
This GLOBAL limiter is based of
https://redis.com/redis-best-practices/basic-rate-limiting/

We implement it with a window in minute to make it easier to test locally but logic is same with hours

Note, this is not exactly a rate limited per hour as we use fixed buckets, but it makes the implementation much simpler
"""
import datetime

import redis

_connection = None


def calc_key(name: str, t: datetime.datetime) -> str:
    key = f"{name}_{t.hour}_{t.minute}"
    return key


class RedisRateLimiter:
    def __init__(self) -> None:
        self.limits = {}

    def add_limit(self, name: str, limit: int) -> None:
        self.limits[name] = limit

    def available(self, pool: redis.ConnectionPool, name: str) -> bool:
        conn = redis.Redis(connection_pool=pool)
        # We get the current hour/minute
        now = datetime.datetime.utcnow()
        key = calc_key(name, now)
        counter = conn.get(key)
        return counter is None or int(counter) <= self.limits[name]

    def increment(self, pool: redis.ConnectionPool, name:str) -> None:
        # only increment if we have a limit
        if name not in self.limits:
            return
        conn = redis.Redis(connection_pool=pool)
        # We get the current hour/minute
        now = datetime.datetime.utcnow()
        key = calc_key(name, now)
        conn.incr(key)
        conn.expire(key, 60)
