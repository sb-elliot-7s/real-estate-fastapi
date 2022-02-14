from auth.auth_repository_interface import AuthRepositoryInterface
from auth.password_interface import PasswordInterface
from auth.schemas import Token
from fastapi import HTTPException, status
from .token_interface import TokenInterface
from settings import get_settings
from .schemas import CreateUserSchema


class AuthServices:
    def __init__(self, repository: AuthRepositoryInterface, password_service: PasswordInterface, token_service: TokenInterface = None):
        self._repository = repository
        self._password_service = password_service
        self._token_service = token_service
        self._settings = get_settings()

    async def _authenticate(self, username: str, password: str):
        if not (user := await self._repository.retrieve_user_by_username(username=username)) \
                or not await self._password_service.verify_password(plain_password=password, hashed_password=user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect username or password')
        return user

    async def sign_up(self, data: CreateUserSchema):
        if await self._repository.retrieve_user_by_username(username=data.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with this username or email exists')
        if await self._repository.retrieve_user_by_email(email=data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with this email exists')
        hashed_password = await self._password_service.hashed_password(password=data.password)
        return await self._repository.save_user(username=data.username, password=hashed_password, email=data.email)

    async def refresh_token(self, refresh_token: str):
        payload = await self._token_service.decode_refresh_token(refresh_token=refresh_token, secret_key=self._settings.secret_key,
                                                                 algorithm=self._settings.algorithm)
        return await self.create_tokens(username=payload.get('sub'))

    async def create_tokens(self, username: str):
        subject = {'sub': username}
        params = {'secret_key': self._settings.secret_key, 'algorithm': self._settings.algorithm}
        access_token: str = await self._token_service.create_token(data=subject, token_type='access_token', **params,
                                                                   exp_time=self._settings.access_token_expire_minutes)
        refresh_token: str = await self._token_service.create_token(data=subject, token_type='refresh_token', **params,
                                                                    exp_time=self._settings.refresh_token_expire_minutes)
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def save_user(self, username: str, password: str) -> Token:
        user = await self._authenticate(username=username, password=password)
        return await self.create_tokens(username=user.username)
