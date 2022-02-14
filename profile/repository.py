from sqlalchemy.engine import Result
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from .repository_interface import ProfileRepositoryInterface


class ProfileRepository(ProfileRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def update_profile(self, updated_data: dict, user: User) -> User:
        result: Result = await self._session.execute(update(User).where(User.id == user.id).values(**updated_data).returning(User))
        await self._session.commit()
        return result.first()

    async def delete_user(self, user: User):
        result: Result = await self._session.execute(delete(User).where(User.id == user.id))
        await self._session.commit()
