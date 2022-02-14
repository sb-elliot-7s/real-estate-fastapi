from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from .schemas import CreateUserSchema, Token, RefreshToken
from .services import AuthServices
from .repositories import AuthRepository
from .password_service import PasswordService
from .token_service import TokenService

from profile.schemas import ResponseUserSchema

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=ResponseUserSchema)
async def sign_up(user_data: CreateUserSchema, db: AsyncSession = Depends(get_db)):
    return await AuthServices(repository=AuthRepository(session=db),
                              password_service=PasswordService(context=CryptContext(schemes=["bcrypt"], deprecated="auto"))) \
        .sign_up(data=user_data)


@auth_router.post('/login', status_code=status.HTTP_200_OK, response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await AuthServices(repository=AuthRepository(session=db), token_service=TokenService(),
                              password_service=PasswordService(context=CryptContext(schemes=['bcrypt'], deprecated='auto'))) \
        .save_user(username=form_data.username, password=form_data.password)


@auth_router.post('/refresh_token', response_model=Token, status_code=status.HTTP_201_CREATED)
async def refresh_token(refresh_token_data: RefreshToken, db: AsyncSession = Depends(get_db)):
    return await AuthServices(repository=AuthRepository(session=db), token_service=TokenService(),
                              password_service=PasswordService(context=CryptContext(schemes=['bcrypt'], deprecated='auto'))) \
        .refresh_token(refresh_token=refresh_token_data.refresh_token)
