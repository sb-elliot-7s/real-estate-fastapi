from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.engine import Result

from database import get_db
from auth.token_interface import TokenInterface
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from profile.models import User
from settings import get_settings


class GetUser:
    OAUTH_TOKEN = OAuth2PasswordBearer(tokenUrl='/auth/login')

    def __init__(self, token_service: TokenInterface):
        self._token_service = token_service
        self._settings = get_settings()

    async def __call__(self, db: AsyncSession = Depends(get_db), token: str = Depends(OAUTH_TOKEN)):
        payload: dict = await self._token_service.decode_access_token(token=token, secret_key=self._settings.secret_key,
                                                                      algorithm=self._settings.algorithm)
        result: Result = await db.execute(select(User).where(User.username == payload.get('sub'), User.is_active))
        return result.scalars().first()
