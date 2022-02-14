from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from .services import ProfileService
from .repository import ProfileRepository
from database import get_db
from permissions import GetUser
from .models import User
from auth.token_service import TokenService
from .schemas import UserUpdateSchema, ResponseUserSchema

profile_router = APIRouter(prefix='/profile', tags=['profile'])


@profile_router.put('/', status_code=status.HTTP_200_OK, response_model=ResponseUserSchema)
async def update_profile(updated_data: UserUpdateSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(GetUser(token_service=TokenService()))):
    return await ProfileService(repository=ProfileRepository(session=db)).update_profile(data=updated_data, user=user)


@profile_router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: AsyncSession = Depends(get_db),
                      user: User = Depends(GetUser(token_service=TokenService()))):
    return await ProfileService(repository=ProfileRepository(session=db)).delete_user(user=user)
