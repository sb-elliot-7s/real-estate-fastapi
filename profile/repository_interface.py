from abc import ABC, abstractmethod

from .models import User
from .schemas import UserUpdateSchema


class ProfileRepositoryInterface(ABC):
    @abstractmethod
    async def update_profile(self, updated_data: dict, user: User) -> User: pass

    @abstractmethod
    async def delete_user(self, user: User): pass
