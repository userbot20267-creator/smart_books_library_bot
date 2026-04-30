"""Review and Rating Schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewSchema(BaseModel):
    """Review response schema"""
    id: int
    book_id: int
    user_id: int
    title: Optional[str] = None
    content: str
    likes_count: int
    replies_count: int
    is_verified_purchase: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewCreateSchema(BaseModel):
    """Review creation schema"""
    book_id: int
    title: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=5000)


class ReviewUpdateSchema(BaseModel):
    """Review update schema"""
    title: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1, max_length=5000)


class RatingSchema(BaseModel):
    """Rating response schema"""
    id: int
    book_id: int
    user_id: int
    rating: int = Field(..., ge=1, le=5)
    created_at: datetime

    class Config:
        from_attributes = True


class RatingCreateSchema(BaseModel):
    """Rating creation schema"""
    book_id: int
    rating: int = Field(..., ge=1, le=5)
