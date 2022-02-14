from typing import Optional
import aiofiles
import pytest
from httpx import AsyncClient
from collections import namedtuple
from settings import get_settings, LISTINGS_IMAGES_DIR


class TestListingsControllers:
    COMMON_DATA = {
        'category_type': 'SELL',
        'title': 'LA California',
        'price': 100_000,
        'city': 'LA',
        'country': 'USA',
        'number_of_rooms': 2,
        'total_area': 32,
        'elevator': True,
        'wall_type': 'BRICK',
        'house_type': 'NEW_BUILDING',
        'description': 'some description'
    }

    AddListing = namedtuple('AddListing', 'country city street region district house_number price title description total_area number_of_floors '
                                          'year_built number_of_rooms category_type house_type wall_type elevator list_images')

    madrid_listing = AddListing(
        country='spain', city='madrid', street='1st', region='region', district='district', house_number='10', price=1000.00, title='new listing',
        description='some description', total_area=65.0, number_of_floors=11, year_built=2020, number_of_rooms=3, category_type='SELL',
        house_type='NEW_BUILDING', wall_type='BRICK', elevator=True, list_images=[get_settings().test_listing_image_path]
    )

    london_listing = AddListing(
        country='gb', city='london', street='1st', region='region', district='district', house_number='10', price=3000.00, title='new listing',
        description='some description', total_area=65, number_of_floors=11, year_built=2020, number_of_rooms=3, category_type='SELL',
        house_type='NEW_BUILDING', wall_type='BRICK', elevator=True,
        list_images=[get_settings().test_listing_image_path, get_settings().test_listing_image_path]
    )
    rome_listing = AddListing(
        country='italy', city='rome', street='1st', region='region', district='district', house_number='10', price=7000.00, title='new listing',
        description='some description', total_area=65, number_of_floors=11, year_built=2020, number_of_rooms=3, category_type='SELL',
        house_type='SECONDARY_HOUSING', wall_type='BRICK', elevator=True, list_images=None
    )

    @pytest.mark.asyncio
    async def test_empty_listings(self, client_without_jwt: AsyncClient):
        response = await client_without_jwt.get(url='/listings/')
        assert response.status_code == 200
        assert len(response.json()) == 0

    @pytest.mark.parametrize('country, city, street, region, district, house_number, price, title, description, total_area, number_of_floors,'
                             'year_built, number_of_rooms, category_type, house_type, wall_type, elevator, list_images, saved_listing_id,'
                             ' count_of_images',
                             [(*madrid_listing, 1, 1), (*london_listing, 2, 2), (*rome_listing, 3, 0)])
    @pytest.mark.asyncio
    async def test_add_listing(self, first_user_client_with_jwt: AsyncClient, list_images, country: str, city: str, street: str, region: str,
                               district: str, house_number: str,
                               price: float, title: str, description: str, total_area: float, number_of_floors: int, year_built: int,
                               number_of_rooms: int, category_type: str, house_type: str, wall_type: str, elevator: bool, saved_listing_id: int,
                               count_of_images: int):
        data = {
            'country': country, 'city': city, 'street': street, 'region': region, 'district': district, 'house_number': house_number, 'price': price,
            'title': title, 'description': description, 'total_area': total_area, 'number_of_floors': number_of_floors, 'year_built': year_built,
            'number_of_rooms': number_of_rooms, 'category_type': category_type, 'house_type': house_type, 'wall_type': wall_type,
            'elevator': elevator
        }
        files = []
        if list_images:
            for image in list_images:
                async with aiofiles.open(image, mode='rb') as file:
                    t = ('files', (image.split('/')[-1], await file.read()))
                    files.append(t)
        response = await first_user_client_with_jwt.post(url='/listings/', data=data, files=files if list_images else None)
        assert response.status_code == 201
        assert response.json()['id'] == saved_listing_id
        assert response.json()['title'] == title
        assert response.json()['country'] == country
        assert len(response.json()['images']) == count_of_images

    @pytest.mark.asyncio
    async def test_add_listing_without_jwt(self, client_without_jwt: AsyncClient):
        res = await client_without_jwt.post(url='/listings/', data=self.COMMON_DATA)
        assert res.status_code == 401
        assert res.json()['detail'] == 'Not authenticated'

    @pytest.mark.parametrize('price, title, category_type, number_of_rooms, total_area, country, city, expected_value',
                             [(None, None, None, None, None, None, None, 'field required')])
    @pytest.mark.asyncio
    async def test_failure_add_listing(self, first_user_client_with_jwt: AsyncClient, price: Optional[float], title: Optional[str],
                                       category_type: Optional[str], number_of_rooms, total_area: Optional[float], country: Optional[str],
                                       city: Optional[str], expected_value: str):
        data = {
            'price': price,
            'title': title,
            'category_type': category_type,
            'number_of_rooms': number_of_rooms,
            'total_area': total_area,
            'country': country, 'city': city
        }
        response = await first_user_client_with_jwt.post(url='/listings/', data=data)
        assert response.status_code == 422
        for i in response.json()['detail']:
            assert i.get('msg') == expected_value

    @pytest.mark.asyncio
    async def test_get_user_listings(self, client_without_jwt: AsyncClient):
        response = await client_without_jwt.get('/listings/user/1')
        assert response.status_code == 200
        assert len(response.json()) == 3

    @pytest.mark.asyncio
    async def test_get_all_listings(self, client_without_jwt: AsyncClient):
        response = await client_without_jwt.get('/listings/')
        assert response.status_code == 200
        assert len(response.json()) == 3

    @pytest.mark.parametrize('house_type, country, min_price, max_price, count_of_listings', [
        ('SECONDARY_HOUSING', 'italy', 5000.0, 8000.0, 1),
        ('NEW_BUILDING', '', 0.0, 5000.0, 2),
        ('NEW_BUILDING', '', 950.0, 2000.0, 1)
    ])
    @pytest.mark.asyncio
    async def test_get_listings_from_query_params(self, client_without_jwt: AsyncClient, house_type, country, min_price, max_price,
                                                  count_of_listings):
        response = await client_without_jwt.get(
            url=f'/listings/?limit=20&offset=0&house_type={house_type}&country={country}&min_price={min_price}&max_price={max_price}')
        assert len(response.json()) == count_of_listings

    @pytest.mark.parametrize('id_, country, city, title', [
        (1, madrid_listing.country, madrid_listing.city, madrid_listing.title),
        (2, london_listing.country, london_listing.city, london_listing.title),
        (3, rome_listing.country, rome_listing.city, rome_listing.title),
    ])
    @pytest.mark.asyncio
    async def test_get_detail_listing(self, client_without_jwt: AsyncClient, id_, country, city, title):
        response = await client_without_jwt.get(f'/listings/{id_}')
        assert response.status_code == 200
        assert response.json()['id'] == id_
        assert response.json()['title'] == title
        assert response.json()['country'] == country
        assert response.json()['city'] == city

    @pytest.mark.asyncio
    async def test_update_article_by_second_user(self, second_user_client_with_jwt: AsyncClient):
        response = await second_user_client_with_jwt.put(url='/listings/1', data=self.COMMON_DATA)
        assert response.status_code == 400
        assert response.json()['detail'] == 'You cannot update this listing'

    @pytest.mark.parametrize('listing_id, status_code, key, value', [
        (1, 200, 'city', 'LA'), (10, 404, 'detail', 'Listing not found')
    ])
    @pytest.mark.asyncio
    async def test_update_listing_or_not_found(self, first_user_client_with_jwt: AsyncClient, listing_id: int, status_code: int, key, value):
        response = await first_user_client_with_jwt.put(url=f'/listings/{listing_id}', data=self.COMMON_DATA)
        assert response.json()[key] == value
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_add_to_favorites(self, first_user_client_with_jwt: AsyncClient):
        response = await first_user_client_with_jwt.post(url='/listings/favorites/1')
        assert response.status_code == 201
        assert response.json() == 'added to favorites'

    @pytest.mark.asyncio
    async def test_show_favorites_listings(self, first_user_client_with_jwt: AsyncClient):
        response = await first_user_client_with_jwt.get(url='/listings/favorites')
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0].get('id') == 1

    @pytest.mark.parametrize('id_, status_code', [(1, 204), (100, 404)])
    @pytest.mark.asyncio
    async def test_remove_from_favorites_or_not_found(self, first_user_client_with_jwt, id_: int, status_code: int):
        response = await first_user_client_with_jwt.delete(url=f'/listings/favorites/{id_}')
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_show_empty_favorites_listings(self, first_user_client_with_jwt: AsyncClient):
        response = await first_user_client_with_jwt.get(url='/listings/favorites')
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.parametrize('listing_id, status_code', [(1, 204), (4, 404)])
    @pytest.mark.asyncio
    async def test_delete_listing_or_not_found(self, first_user_client_with_jwt: AsyncClient, listing_id: int, status_code: int):
        response = await first_user_client_with_jwt.delete(url=f'/listings/{listing_id}')
        assert response.status_code == status_code

    @pytest.mark.asyncio
    async def test_not_found_listing(self, client_without_jwt: AsyncClient):
        response = await client_without_jwt.get(url='/listings/100')
        assert response.status_code == 404
        assert response.json()['detail'] == 'Listing not found'

    @pytest.mark.asyncio
    async def test_delete_images_from_local_folder_after_tests(self):
        from image_service.local_image_service import ImageService
        image_service = ImageService(path=str(LISTINGS_IMAGES_DIR))
        for i in LISTINGS_IMAGES_DIR.iterdir():
            img_name = f'{i}'.split('/')[-1]
            await image_service.delete_image(filename=img_name)
