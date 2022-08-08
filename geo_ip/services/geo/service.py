from typing import Dict, List

from geo_ip.geo.geo_location import GeoLocation, IPAddress
from geo_ip.services.geo.fetcher import Fetcher


class Service:
    def __init__(self):
        self.fetchers: Dict[str, Fetcher] = {}

    def add(self, name: str, params: Dict[str, str]):
        # build the fetcher
        fetcher = Fetcher.build(name, params)
        self.fetchers[name] = fetcher

    def look_up(self, fetchers: List[str], ip: IPAddress) -> (GeoLocation, str):
        for fetcher in fetchers:
            try:
                geo = self.fetchers[fetcher].fetch(ip)
                geo.meta["source"] = fetcher
                return geo, fetcher
            except Exception:
                pass
