import pickle
from typing import Optional

import redis

from geo_ip.geo.geo_location import GeoLocation, IPAddress


def key(ip: IPAddress) -> str:
    return f"g_{ip}"


class RedisCache:
    def __init__(self):
        self.in_memory = {}

    def get(self, pool: redis.ConnectionPool, ip: IPAddress) -> Optional[GeoLocation]:
        if ip in self.in_memory:
            geo = self.in_memory[ip]
            geo.meta["cached"] = "in_memory"
            return geo
        try:
            conn = redis.Redis(connection_pool=pool)
            value = conn.get(key(ip))
            if value is None:
                return None
            geo = pickle.loads(value)
            self.in_memory[ip] = geo
            geo.meta["cached"] = "redis"
        except redis.exceptions.ConnectionError:
            return None
        return geo

    def set(self, pool: redis.ConnectionPool, ip: IPAddress, geo: GeoLocation):
        self.in_memory[ip] = geo
        try:
            conn = redis.Redis(connection_pool=pool)
            conn.set(key(ip), pickle.dumps(geo))
            # For debugging only
            conn.expire(key(ip), 120)
        except redis.exceptions.ConnectionError:
            pass
