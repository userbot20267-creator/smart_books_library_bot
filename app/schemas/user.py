"""User Schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserSchema(BaseModel):
    """User response schema"""
    id: int
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    status: str
    is_premium: bool
    language: str
    total_downloads: int
    total_books_read: int
    level: int
    created_at: datetime
    updated_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    """User creation schema"""
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    language: str = "ar"


class UserUpdateSchema(BaseModel):
    """User update schema"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    language: Optional[str] = None
    notification_enabled: Optional[bool] = None


class UserProfileSchema(BaseModel):
    """User profile schema"""
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    is_premium: bool
    level: int
    total_downloads: int
    total_books_read: int

    class Config:
        from_attributes = True
