from typing import Optional
from abc import ABC, abstractmethod
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter


class GeoInterface(ABC):
    @abstractmethod
    async def get_longitude_and_latitude(self, country: str, city: str, street: str, house_number: Optional[str]):
        pass

    @abstractmethod
    async def get_address_from_latitude_longitude(self, latitude: float, longitude: float): ...


class Geo(GeoInterface):
    def __init__(self):
        self.nominatim = Nominatim(user_agent='real_estate', adapter_factory=AioHTTPAdapter)

    async def get_address_from_latitude_longitude(self, latitude: str, longitude: str):
        async with self.nominatim as geo:
            coord = f'{latitude}, {longitude}'
            loc = await geo.reverse(coord, language='ru_RU')
            return loc.address

    async def get_longitude_and_latitude(self, country: str, city: str, street: str, house_number: Optional[str] = None):
        async with self.nominatim as geo:
            address = f'{house_number}, {street}, {city}, {country}' if house_number else f'{street}, {city}, {country}'
            location_ = await geo.geocode(address)
            return location_.latitude, location_.longitude, str(location_)
