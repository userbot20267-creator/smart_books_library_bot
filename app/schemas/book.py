"""Book Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategorySchema(BaseModel):
    """Category schema"""
    id: int
    name: str
    name_ar: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    order: int

    class Config:
        from_attributes = True


class BookSchema(BaseModel):
    """Book response schema"""
    id: int
    title: str
    author: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    file_type: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    pages: Optional[int] = None
    language: str
    cover_image_url: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_tags: Optional[str] = None
    download_count: int
    view_count: int
    average_rating: float
    total_reviews: int
    status: str
    is_featured: bool
    is_exclusive: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BookDetailSchema(BookSchema):
    """Detailed book schema"""
    ai_classification: Optional[str] = None
    total_likes: int
    updated_at: datetime


class BookCreateSchema(BaseModel):
    """Book creation schema"""
    title: str
    author: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    pages: Optional[int] = None
    language: str = "ar"
    file_type: str = "pdf"


class BookUpdateSchema(BaseModel):
    """Book update schema"""
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    pages: Optional[int] = None
    is_featured: Optional[bool] = None
    is_exclusive: Optional[bool] = None
    status: Optional[str] = None


class BookSearchSchema(BaseModel):
    """Book search schema"""
    query: str = Field(..., min_length=1, max_length=255)
    search_type: str = "text"  # text, semantic, ocr
    category_id: Optional[int] = None
    language: Optional[str] = None
    sort_by: str = "relevance"  # relevance, rating, downloads, newest
    limit: int = Field(20, le=100)
    offset: int = Field(0, ge=0)
