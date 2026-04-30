"""Book API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.book_service import BookService
from app.schemas.book import BookSchema, BookDetailSchema, BookCreateSchema
from app.models.book import Book

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("/", response_model=List[BookSchema])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of books with pagination"""
    books = db.query(Book).offset(skip).limit(limit).all()
    return books


@router.get("/featured", response_model=List[BookSchema])
async def get_featured_books(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured books"""
    service = BookService(db)
    books = await service.get_featured_books(limit)
    return books


@router.get("/trending", response_model=List[BookSchema])
async def get_trending_books(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending books"""
    service = BookService(db)
    books = await service.get_trending_books(limit)
    return books


@router.get("/category/{category_id}", response_model=List[BookSchema])
async def get_books_by_category(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get books by category"""
    service = BookService(db)
    books = await service.get_books_by_category(category_id, limit, skip)
    return books


@router.get("/{book_id}", response_model=BookDetailSchema)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get book details"""
    service = BookService(db)
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookSchema)
async def create_book(
    book_data: BookCreateSchema,
    db: Session = Depends(get_db)
):
    """Create new book"""
    service = BookService(db)
    book = await service.create_book(book_data)
    if not book:
        raise HTTPException(status_code=400, detail="Failed to create book")
    return book


@router.get("/{book_id}/download")
async def download_book(book_id: int, db: Session = Depends(get_db)):
    """Download book file"""
    service = BookService(db)
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if not book.file_path:
        raise HTTPException(status_code=400, detail="Book file not available")
    
    # Increment download count
    await service.increment_download_count(book_id)
    
    return {"file_path": book.file_path, "file_type": book.file_type}
