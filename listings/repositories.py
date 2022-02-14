from typing import Optional
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from image_service.image_service_interface import ImageServiceInterface
from profile.models import User
from .repository_interface import RepositoryInterface
from .models import Listing, Image, Favorite
from fastapi import HTTPException, status, UploadFile
import uuid
from .query_filter_service import QueryListingParamsService


class RepositoryListing(RepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def _add_image(self, files: Optional[list[UploadFile]], listing_id: int, file_service: ImageServiceInterface):
        if files:
            for image in files:
                filename = f'{uuid.uuid4()}.{image.filename}'
                await file_service.write_image(file=image, filename=filename)
                await self._session.execute(insert(Image).values(photo=filename, listing_id=listing_id))

    async def add_listing(self, listing_data: dict, user: User, files: Optional[list[UploadFile]], file_service: ImageServiceInterface) -> Listing:
        listing_result = await self._session.execute(
            insert(Listing).values(**listing_data, user_id=user.id).returning(Listing.id))
        listing_id: Listing = listing_result.scalars().first()
        await self._add_image(files=files, listing_id=listing_id, file_service=file_service)
        await self._session.commit()
        listing = await self._session.execute(select(Listing).where(Listing.id == listing_id))
        return listing.scalars().first()

    async def update_listing(self, listing_id: int, updated_data: dict, user: User, files: Optional[list[UploadFile]],
                             file_service: ImageServiceInterface) -> tuple[bool, Optional[Listing]]:
        if (listing := await self.get_single_listing(listing_id=listing_id)) and listing.user_id != user.id:
            return False, None
        await self._add_image(files=files, listing_id=listing_id, file_service=file_service)
        _ = await self._session.execute(update(Listing).where(Listing.id == listing.id).values(**updated_data).returning(Listing))
        await self._session.commit()
        await self._session.refresh(listing)
        return True, listing

    async def get_single_listing(self, listing_id: int) -> Listing:
        result = await self._session.execute(select(Listing).filter_by(id=listing_id))
        if not (listing := result.scalars().first()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Listing not found')
        return listing

    async def get_user_listings(self, user_id: int, offset: int, limit: int):
        result = await self._session.execute(select(Listing).where(Listing.user_id == user_id).limit(limit).offset(offset))
        return result.scalars().unique().all()

    async def get_all_listings(self, offset: int, limit: int, base_building_params: dict, advanced_building_params: dict, price_params: dict,
                               address_params: dict) -> list[Listing]:
        query_service = QueryListingParamsService()
        stmt = select(Listing)
        stmt = await query_service.common_address_params(stm=stmt, address_params=address_params)
        stmt = await query_service.advanced_building_params(stm=stmt, advanced_building_params=advanced_building_params)
        stmt = await query_service.price_params(stm=stmt, price_params=price_params)
        result = await self._session.execute(
            stmt.filter_by(**base_building_params).order_by(Listing.updated.desc()).limit(limit).offset(offset))
        return result.scalars().unique().all()

    async def get_detail_listing(self, listing_id: int) -> Listing:
        return await self.get_single_listing(listing_id=listing_id)

    async def delete_listing(self, listing_id: int, user: User, file_service: ImageServiceInterface):
        listing = await self.get_single_listing(listing_id=listing_id)
        if listing.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot delete this listing')
        if listing.images:
            for image in listing.images:
                await file_service.delete_image(filename=image.photo)
        await self._session.delete(listing)
        await self._session.commit()

    async def add_to_favorites(self, listing_id: int, user: User) -> bool:
        listing = await self.get_single_listing(listing_id=listing_id)
        _ = await self._session.execute(insert(Favorite).values(listing_id=listing.id, user_id=user.id, is_favorite=True))
        await self._session.commit()
        return True

    async def remove_from_favorites(self, favorite_id: int, user: User):
        res = await self._session.execute(select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == user.id))
        if not (favorite := res.scalars().first()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Favorite not found')
        await self._session.delete(favorite)
        await self._session.commit()

    async def show_favorites_listings(self, offset: int, limit: int, user: User):
        stmt = select(Listing).join(Favorite).where(Favorite.user_id == user.id, Favorite.is_favorite).offset(offset).limit(limit) \
            .order_by(Listing.updated.desc())
        res = await self._session.execute(stmt)
        return res.scalars().unique().all()
