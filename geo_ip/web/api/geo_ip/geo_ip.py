from ipaddress import ip_address

import httpx
from fastapi import APIRouter, HTTPException, Request

from geo_ip.geo.geo_location import GeoLocation
from geo_ip.services.geo.service import LimitedError, Service
from geo_ip.settings import settings

router = APIRouter()

service = Service()

for fetcher, params in settings.fetchers:
    service.add(fetcher, params)


@router.get("/geo_ip/{ip}")
def geo_ip(ip: str, request: Request) -> GeoLocation:
    """handler."""
    try:
        ip_addr = ip_address(str(ip))
        # NOT super happy about passing the redis pool but couldn't find a way
        return service.look_up(request.app.state.redis_pool, ip_addr)
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
