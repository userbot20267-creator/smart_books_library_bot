"""Review API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.book_service import BookService
from app.schemas.review import ReviewSchema, ReviewCreateSchema, RatingSchema, RatingCreateSchema

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/book/{book_id}", response_model=List[ReviewSchema])
async def get_book_reviews(
    book_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get reviews for a book"""
    from app.models.review import Review
    reviews = db.query(Review).filter(Review.book_id == book_id).offset(skip).limit(limit).all()
    return reviews


@router.post("/", response_model=ReviewSchema)
async def create_review(
    review_data: ReviewCreateSchema,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Create a review"""
    service = BookService(db)
    review = await service.add_review(
        review_data.book_id,
        user_id,
        review_data.title,
        review_data.content
    )
    if not review:
        raise HTTPException(status_code=400, detail="Failed to create review")
    return review


@router.get("/ratings/book/{book_id}", response_model=List[RatingSchema])
async def get_book_ratings(
    book_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get ratings for a book"""
    from app.models.review import Rating
    ratings = db.query(Rating).filter(Rating.book_id == book_id).offset(skip).limit(limit).all()
    return ratings


@router.post("/ratings", response_model=RatingSchema)
async def create_rating(
    rating_data: RatingCreateSchema,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Create a rating"""
    service = BookService(db)
    rating = await service.add_rating(rating_data.book_id, user_id, rating_data.rating)
    if not rating:
        raise HTTPException(status_code=400, detail="Failed to create rating")
    return rating
