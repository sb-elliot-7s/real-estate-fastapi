from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from permissions import GetUser
from settings import LISTINGS_IMAGES_DIR
from profile.models import User
from auth.token_service import TokenService
from .service import ListingsService
from .repositories import RepositoryListing
from .schemas import UpdateListingSchema, CreateListingSchema, ListingSchema, BaseAddressSchema, PriceQuerySchema, BuildingQuerySchema, \
    BaseBuildingSchema
from .dependencies import LimitOffsetQueryParams
from image_service.local_image_service import ImageService
from .utils import Geo

listings_router = APIRouter(prefix='/listings', tags=['listings'])


@listings_router.get('/user/{user_id}', status_code=status.HTTP_200_OK, response_model=list[ListingSchema])
async def get_user_listings(user_id: int, commons: LimitOffsetQueryParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await ListingsService(repository=RepositoryListing(session=db)) \
        .get_user_listings(user_id=user_id, limit=commons.limit, offset=commons.offset)


@listings_router.get('/', status_code=status.HTTP_200_OK, response_model=list[ListingSchema])
async def get_listings(commons: LimitOffsetQueryParams = Depends(),
                       address_params: BaseAddressSchema = Depends(BaseAddressSchema.as_query),
                       base_building_params: BaseBuildingSchema = Depends(BaseBuildingSchema.as_query),
                       advanced_building_params: BuildingQuerySchema = Depends(BuildingQuerySchema.as_query),
                       price_params: PriceQuerySchema = Depends(PriceQuerySchema.as_query),
                       db: AsyncSession = Depends(get_db)):
    return await ListingsService(repository=RepositoryListing(session=db)) \
        .get_all_listings(limit=commons.limit, offset=commons.offset, base_building_params=base_building_params,
                          advanced_building_params=advanced_building_params, price_params=price_params, address_params=address_params)


@listings_router.get('/favorites', status_code=status.HTTP_200_OK, response_model=list[ListingSchema])
async def show_favorites_listings(commons: LimitOffsetQueryParams = Depends(), db: AsyncSession = Depends(get_db),
                                  user: User = Depends(GetUser(token_service=TokenService()))):
    return await ListingsService(repository=RepositoryListing(session=db)) \
        .show_favorites_listings(offset=commons.offset, limit=commons.limit, user=user)


@listings_router.post('/', response_model=ListingSchema, status_code=status.HTTP_201_CREATED)
async def add_listing(listing: CreateListingSchema = Depends(CreateListingSchema.as_form),
                      address: BaseAddressSchema = Depends(BaseAddressSchema.as_form), files: Optional[list[UploadFile]] = File(None),
                      db: AsyncSession = Depends(get_db), user: User = Depends(GetUser(token_service=TokenService()))):
    return await ListingsService(repository=RepositoryListing(session=db)) \
        .add_listing(listing=listing, address=address, files=files, user=user, file_service=ImageService(path=str(LISTINGS_IMAGES_DIR)), geo=Geo())


@listings_router.put('/{listing_id}', status_code=status.HTTP_200_OK, response_model=ListingSchema)
async def update_listing(listing_id: int, updated_listing: UpdateListingSchema = Depends(UpdateListingSchema.as_form),
                         updated_address: BaseAddressSchema = Depends(BaseAddressSchema.as_form),
                         files: Optional[list[UploadFile]] = Form(None), db: AsyncSession = Depends(get_db),
                         user: User = Depends(GetUser(token_service=TokenService()))):
    return await ListingsService(repository=RepositoryListing(session=db)) \
        .update_listing(listing_id=listing_id, listing=updated_listing, address=updated_address, user=user, files=files,
                        file_service=ImageService(path=str(LISTINGS_IMAGES_DIR)), geo=Geo())


@listings_router.delete('/{listing_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(listing_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(GetUser(token_service=TokenService()))):
    return await ListingsService(repository=RepositoryListing(session=db)).delete_listing(listing_id=listing_id, user=user,
                                                                                          file_service=ImageService(path=str(LISTINGS_IMAGES_DIR)))


@listings_router.get('/{listing_id}', response_model=ListingSchema, status_code=status.HTTP_200_OK)
async def detail_listing(listing_id: int, db: AsyncSession = Depends(get_db)):
    return await ListingsService(repository=RepositoryListing(session=db)).detail_listing(listing_id=listing_id)


@listings_router.post('/favorites/{listing_id}', status_code=status.HTTP_201_CREATED)
async def add_to_favorites(listing_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(GetUser(token_service=TokenService()))):
    return await ListingsService(repository=RepositoryListing(session=db)).add_to_favorites(listing_id=listing_id, user=user)


@listings_router.delete('/favorites/{favorite_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(favorite_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(GetUser(token_service=TokenService()))):
    return await ListingsService(repository=RepositoryListing(session=db)).remove_from_favorites(favorite_id=favorite_id, user=user)
