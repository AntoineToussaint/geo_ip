from ipaddress import ip_address

import httpx
from fastapi import APIRouter, HTTPException, Request
import socket

from geo_ip.geo.geo_location import GeoLocation

import geo_ip.services.geo
from geo_ip.services.geo.service import Service
from geo_ip.services.cache.redis_cache import RedisCache
from geo_ip.services.rate_limiters.redis_rate_limiter import RedisRateLimiter

from geo_ip.settings import settings

RATE_LIMIT = "rate_limit"


class LimitedError(Exception):
    pass


router = APIRouter()

service = Service()

cache = RedisCache()

limiter = RedisRateLimiter()

for fetcher, params in settings.fetchers:
    service.add(fetcher, params)
    if RATE_LIMIT in params:
        limiter.add_limit(fetcher, int(params[RATE_LIMIT]))


def host() -> str:
    return socket.gethostbyname(socket.gethostname())


@router.get("/geo_ip/{ip}")
def geo_ip(ip: str, request: Request) -> GeoLocation:
    """handler."""
    pool = request.app.state.redis_pool
    try:
        ip_addr = ip_address(str(ip))
        # Look in cache
        cached = cache.get(pool, ip_addr)
        if cached:
            cached.meta["host"] = host()
            return cached
        # What fetchers are available
        available = limiter.all_available(pool)
        if len(available) == 0:
            raise LimitedError
        geo, source = service.look_up(available, ip_addr)
        cache.set(pool, ip_addr, geo)
        limiter.increment(pool, source)

        return geo
    except LimitedError:
        raise HTTPException(
            status_code=httpx.codes.INTERNAL_SERVER_ERROR,
            detail="No  fetcher available",
        )
    except ValueError:
        raise HTTPException(
            status_code=httpx.codes.BAD_REQUEST,
            detail="Not a valid IP",
        )
