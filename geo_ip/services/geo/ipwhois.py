from typing import Dict

import requests

from geo_ip.geo.geo_location import GeoLocation, IPAddress

from .fetcher import Fetcher


class IPWhoIs(Fetcher):
    def __init__(self, params: Dict[str, str]):
        pass

    @staticmethod
    def name() -> str:
        return "ipwhois"

    def fetch(self, ip: IPAddress) -> GeoLocation:
        url = f"http://ipwho.is/{ip}"
        print(url)
        r = requests.get(url).json()
        return GeoLocation(country=r["country"])


Fetcher.register(IPWhoIs)
