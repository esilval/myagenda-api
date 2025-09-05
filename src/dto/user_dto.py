from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    nickname: str | None = Field(default=None, max_length=50)
    password: str = Field(min_length=8, max_length=255)
    company: str | None = Field(default=None, max_length=100)


class UserDTO(UserCreateDTO):
    id: str
    created_at: datetime
    updated_at: datetime


class UserUpdateDTO(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    nickname: str | None = Field(default=None, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=255)
    company: str | None = Field(default=None, max_length=100)


class UserReadDTO(BaseModel):
    id: str
    name: str
    email: EmailStr
    nickname: str | None
    company: str | None
    status: str
    created_at: datetime
    updated_at: datetime

