from .models import User
from .repository_interface import ProfileRepositoryInterface
from .schemas import UserUpdateSchema
from fastapi import status, Response


class ProfileService:
    def __init__(self, repository: ProfileRepositoryInterface):
        self._repository = repository

    async def update_profile(self, data: UserUpdateSchema, user: User):
        updated_data = data.dict(exclude_none=True)
        return await self._repository.update_profile(updated_data=updated_data, user=user)

    async def delete_user(self, user: User):
        return await self._repository.delete_user(user=user)
