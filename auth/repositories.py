from typing import Optional
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from auth.auth_repository_interface import AuthRepositoryInterface
from profile.models import User


class AuthRepository(AuthRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def retrieve_user_by_username(self, username: str) -> User:
        stmt = select(User).where(User.username == username)
        response = await self._session.execute(stmt)
        return response.scalars().first()

    async def retrieve_user_by_email(self, email: str) -> User:
        if email:
            stmt = select(User).where(User.email == email)
            response = await self._session.execute(stmt)
            return response.scalars().first()

    # async def retrieve_user_by_params(self, params: dict) -> User:
    #     print('params', params)
    #     stmt = select(User).where((User.username == params.get('username')) & (User.email is not None) | (User.email == params.get('email')))
    #     res = await self._session.execute(stmt)
    #     return res.scalars().first()

    async def save_user(self, username: str, password: str, email: Optional[str]) -> User:
        res = await self._session.execute(insert(User).values(username=username, password=password, email=email).returning(User))
        await self._session.commit()
        return res.first()
