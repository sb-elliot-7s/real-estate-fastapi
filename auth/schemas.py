from typing import Optional

from pydantic import BaseModel, Field, EmailStr
from profile.schemas import UserBaseSchema


class RefreshToken(BaseModel):
    refresh_token: str


class Token(RefreshToken):
    access_token: str

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: str = Field(..., min_length=10)

