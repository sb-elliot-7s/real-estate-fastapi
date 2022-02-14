import pytest

from ..utils import Geo
from collections import namedtuple


class TestGeoUtils:
    Address = namedtuple('Address', 'country city street house_number')

    WASHINGTON = Address(country='Соединённые Штаты Америки', city='Вашингтон,', street='Southeast', house_number='202')
    NEW_YORK = Address(country='Соединённые Штаты Америки', city='Нью-Йорк', street='Уолл стрит', house_number='60')

    @pytest.fixture()
    def _get_geo(self):
        return Geo()

    @pytest.mark.parametrize('latitude, longitude, country, city, street, house_number', [
        ('40.70606047881325', '-74.00880414434951', *NEW_YORK),
        ('38.87656716217848', '-77.00359788800425', *WASHINGTON)
    ])
    @pytest.mark.asyncio
    async def test_get_address_from_latitude_longitude(self, _get_geo, latitude: str, longitude: str, country: str, city: str, street: str,
                                                       house_number: str):
        # _geo = Geo()
        address = await _get_geo.get_address_from_latitude_longitude(latitude=latitude, longitude=longitude)
        assert country in address
        assert city in address
        assert street in address
        assert house_number in address

    ny_exp = (40.706173050000004, -74.00851619618786,
              '60 Wall Street, 60, Wall Street, Manhattan Community Board 1, Manhattan, New York, 10005, United States')
    washington_exp = (46.03910555, -118.38584875000001,
                      '202, Southeast 11th Street, College Place, Walla Walla County, Washington, 99324, United States')

    @pytest.mark.parametrize('country, city, street, house_number, expected_values', [
        (NEW_YORK.country, NEW_YORK.city, NEW_YORK.street, NEW_YORK.house_number, ny_exp),
        (WASHINGTON.country, WASHINGTON.city, WASHINGTON.street, WASHINGTON.house_number, washington_exp),
    ])
    @pytest.mark.asyncio
    async def test_get_longitude_and_latitude(self, _get_geo, country: str, city: str, street: str, house_number: str, expected_values):
        point = await _get_geo.get_longitude_and_latitude(country=country, city=city, street=street, house_number=house_number)
        assert point == expected_values
