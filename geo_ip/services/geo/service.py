import socket
from typing import Dict

from geo_ip.geo.geo_location import GeoLocation, IPAddress
from geo_ip.services.cache.redis_cache import RedisCache
from geo_ip.services.geo.fetcher import Fetcher
from geo_ip.services.rate_limiters.redis_rate_limiter import RedisRateLimiter

RATE_LIMIT = "rate_limit"


class LimitedError(Exception):
    pass


class Service:
    def __init__(self):
        self.fetchers: Dict[str, Fetcher] = {}
        # Could be based on configuration as well
        # Factory method here or before
        self.limiter = RedisRateLimiter()
        self.cache = RedisCache()
        self.host = socket.gethostbyname(socket.gethostname())

    def add(self, name: str, params: Dict[str, str]):
        # build the fetcher
        fetcher = Fetcher.build(name, params)
        self.fetchers[name] = fetcher
        # Add rate limits if required
        if RATE_LIMIT in params:
            self.limiter.add_limit(name, int(params[RATE_LIMIT]))

    def look_up(self, pool, ip: IPAddress) -> GeoLocation:
        # Look up in Cache
        cached = self.cache.get(pool, ip)
        if cached:
            cached.meta["host"] = self.host
            return cached

        # Find available fetchers
        available = [
            name for name in self.fetchers.keys() if self.limiter.available(pool, name)
        ]
        if len(available) == 0:
            raise LimitedError
        # We loop over the fetchers
        for name in available:
            try:
                geo = self.fetchers[name].fetch(ip)
                self.limiter.increment(pool, name)
                geo.meta["source"] = name
                self.cache.set(pool, ip, geo)
                geo.meta["host"] = self.host
                return geo
            except Exception:
                pass
