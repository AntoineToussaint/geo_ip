from typing import Dict

from geo_ip.geo.geo_location import GeoLocation, IPAddress

from .fetcher import Fetcher


class Dummy(Fetcher):
    def __init__(self, params: Dict[str, str]):
        pass

    @staticmethod
    def name() -> str:
        return "dummy"

    def fetch(self, ip: IPAddress) -> GeoLocation:
        return GeoLocation(country="France")


Fetcher.register(Dummy)
