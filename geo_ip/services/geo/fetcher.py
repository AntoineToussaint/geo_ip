from abc import ABC, abstractmethod
from typing import Dict

from geo_ip.geo.geo_location import GeoLocation, IPAddress

fetchers = {}


class Fetcher(ABC):
    @staticmethod
    def name() -> str:
        pass

    @staticmethod
    def register(klass):
        fetchers[klass.name()] = klass

    @staticmethod
    def build(name: str, params: Dict[str, str]) -> "Fetcher":
        klass = fetchers.get(name)
        if not klass:
            raise Exception(f"{name} is not a registered fetcher")
        return klass(params)

    @abstractmethod
    def fetch(self, ip: IPAddress) -> GeoLocation:
        pass
