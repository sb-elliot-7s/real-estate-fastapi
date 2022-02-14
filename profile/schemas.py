from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
    username: str = Field(..., max_length=255, min_length=4)
    email: Optional[EmailStr]


class UserUpdateSchema(UserBaseSchema):
    username: Optional[str] = Field(None, max_length=255, min_length=4)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str]


class ResponseUserSchema(UserUpdateSchema):
    id: int
    is_active: bool
    created: datetime
    updated: datetime

    class Config:
        json_encoders = {datetime: lambda f: f.strftime('%Y-%m-%d %H:%M')}
        orm_mode = True
