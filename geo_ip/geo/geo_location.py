from ipaddress import IPv4Address, IPv6Address
from typing import Dict, Optional, Union

from pydantic import BaseModel

IPAddress = Union[IPv4Address, IPv6Address]


class GeoLocation(BaseModel):
    country: str
    meta: Optional[Dict[str, str]] = {}

    # TODO: Add validator country code
    # Easy to do with pydantic
