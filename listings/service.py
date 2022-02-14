from profile.models import User
from .repository_interface import RepositoryInterface
from .schemas import CreateListingSchema, UpdateListingSchema, BaseAddressSchema, PriceQuerySchema, BuildingQuerySchema, BaseBuildingSchema

from typing import Optional
from fastapi import UploadFile, status, HTTPException
from fastapi.responses import JSONResponse, Response
from image_service.image_service_interface import ImageServiceInterface
from utils.create_slug import create_slug
from .utils import GeoInterface


class ListingsService:
    def __init__(self, repository: RepositoryInterface):
        self._repository = repository

    async def get_all_listings(self, limit: int, offset: int, base_building_params: BaseBuildingSchema, advanced_building_params: BuildingQuerySchema,
                               price_params: PriceQuerySchema, address_params: BaseAddressSchema):
        advanced_building_data = advanced_building_params.dict(exclude_none=True)
        base_building_data = base_building_params.dict(exclude_none=True)
        price_data = price_params.dict(exclude_none=True)
        address_data = address_params.dict(exclude_none=True)
        return await self._repository.get_all_listings(limit=limit, offset=offset, base_building_params=base_building_data,
                                                       advanced_building_params=advanced_building_data, address_params=address_data,
                                                       price_params=price_data)

    async def get_user_listings(self, user_id: int, limit: int, offset: int):
        return await self._repository.get_user_listings(user_id=user_id, limit=limit, offset=offset)

    async def detail_listing(self, listing_id: int):
        return await self._repository.get_detail_listing(listing_id=listing_id)

    @staticmethod
    async def _listing_address_update(listing: dict, address: BaseAddressSchema, geo: GeoInterface):
        if listing.get('title'):
            slug = create_slug(text=listing.get('title'))
            listing.update({'slug': slug})
        lat, lng, full_address = await geo.get_longitude_and_latitude(**address.dict(exclude={'region', 'district'}))
        listing.update({'latitude': lat, 'longitude': lng, 'full_address': full_address, **address.dict(exclude_none=True)})

    async def add_listing(self, listing: CreateListingSchema, address: BaseAddressSchema, user: User, files: Optional[list[UploadFile]],
                          file_service: ImageServiceInterface, geo: GeoInterface):
        listing_data_ = listing.dict()
        await self._listing_address_update(listing=listing_data_, address=address, geo=geo)
        return await self._repository.add_listing(listing_data=listing_data_, user=user, files=files, file_service=file_service)

    async def update_listing(self, listing_id: int, listing: UpdateListingSchema, address: BaseAddressSchema, user: User,
                             files: Optional[list[UploadFile]], file_service: ImageServiceInterface, geo: GeoInterface):
        listing_data_ = listing.dict(exclude_none=True)
        await self._listing_address_update(listing=listing_data_, address=address, geo=geo)
        result, listing = await self._repository.update_listing(listing_id=listing_id, updated_data=listing_data_, user=user, files=files,
                                                                file_service=file_service)
        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot update this listing')
        return listing

    async def delete_listing(self, listing_id: int, user: User, file_service: ImageServiceInterface):
        await self._repository.delete_listing(listing_id=listing_id, user=user, file_service=file_service)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def add_to_favorites(self, listing_id: int, user: User):
        _: bool = await self._repository.add_to_favorites(listing_id=listing_id, user=user)
        return JSONResponse(content='added to favorites', status_code=status.HTTP_201_CREATED)

    async def remove_from_favorites(self, favorite_id: int, user: User):
        await self._repository.remove_from_favorites(favorite_id=favorite_id, user=user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def show_favorites_listings(self, offset: int, limit: int, user: User):
        return await self._repository.show_favorites_listings(offset=offset, limit=limit, user=user)
