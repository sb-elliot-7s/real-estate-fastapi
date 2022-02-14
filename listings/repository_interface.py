from abc import ABC, abstractmethod
from image_service.image_service_interface import ImageServiceInterface
from .models import Listing
from profile.models import User
from typing import Optional
from fastapi import UploadFile


class RepositoryInterface(ABC):
    @abstractmethod
    async def get_all_listings(self, offset: int, limit: int, base_building_params: dict, advanced_building_params: dict, price_params: dict,
                               address_params: dict) -> list[Listing]: pass

    @abstractmethod
    async def get_single_listing(self, listing_id: int) -> Listing: pass

    @abstractmethod
    async def get_detail_listing(self, listing_id: int) -> Listing: pass

    @abstractmethod
    async def get_user_listings(self, user_id: int, offset: int, limit: int): pass

    @abstractmethod
    async def add_listing(self, listing_data: dict, user: User, files: Optional[list[UploadFile]],
                          file_service: ImageServiceInterface) -> Listing: pass

    @abstractmethod
    async def update_listing(self, listing_id: int, updated_data: dict, user: User, files: Optional[list[UploadFile]],
                             file_service: ImageServiceInterface) -> tuple[bool, Optional[Listing]]: pass

    @abstractmethod
    async def delete_listing(self, listing_id: int, user: User, file_service: ImageServiceInterface): pass

    @abstractmethod
    async def add_to_favorites(self, listing_id: int, user: User) -> bool: pass

    @abstractmethod
    async def remove_from_favorites(self, favorite_id: int, user: User): pass

    @abstractmethod
    async def show_favorites_listings(self, offset: int, limit: int, user: User): pass
