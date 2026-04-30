"""Search API Endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.search_service import SearchService
from app.schemas.book import BookSchema

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/text", response_model=List[BookSchema])
async def text_search(
    query: str = Query(..., min_length=1, max_length=255),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Text search for books"""
    service = SearchService(db)
    books = await service.text_search(query, limit, skip)
    return books


@router.get("/semantic", response_model=List[BookSchema])
async def semantic_search(
    query: str = Query(..., min_length=1, max_length=255),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Semantic search for books"""
    service = SearchService(db)
    books = await service.semantic_search(query, limit, skip)
    return books


@router.get("/ocr", response_model=List[BookSchema])
async def ocr_search(
    image_text: str = Query(..., min_length=1, max_length=1000),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """OCR-based search for books"""
    service = SearchService(db)
    books = await service.ocr_search(image_text, limit, skip)
    return books


@router.get("/advanced", response_model=List[BookSchema])
async def advanced_search(
    query: str = Query(None, max_length=255),
    category_id: int = Query(None),
    author: str = Query(None, max_length=255),
    language: str = Query(None, max_length=10),
    sort_by: str = Query("relevance", regex="^(relevance|rating|downloads|newest)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Advanced search with multiple filters"""
    service = SearchService(db)
    books = await service.advanced_search(
        query=query,
        category_id=category_id,
        author=author,
        language=language,
        sort_by=sort_by,
        limit=limit,
        offset=skip
    )
    return books
