"""Points API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.points_service import PointsService
from app.schemas.points import UserPointsSchema, PointsTransactionSchema

router = APIRouter(prefix="/api/points", tags=["points"])


@router.get("/user/{user_id}", response_model=UserPointsSchema)
async def get_user_points(user_id: int, db: Session = Depends(get_db)):
    """Get user points"""
    service = PointsService(db)
    user_points = await service.get_user_points(user_id)
    if not user_points:
        raise HTTPException(status_code=404, detail="User points not found")
    return user_points


@router.get("/user/{user_id}/history", response_model=List[PointsTransactionSchema])
async def get_points_history(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get user points transaction history"""
    service = PointsService(db)
    transactions = await service.get_transaction_history(user_id, limit, skip)
    return transactions


@router.get("/leaderboard", response_model=List[UserPointsSchema])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get points leaderboard"""
    service = PointsService(db)
    leaderboard = await service.get_leaderboard(limit)
    return leaderboard


@router.post("/user/{user_id}/reward/download/{book_id}")
async def reward_download(
    user_id: int,
    book_id: int,
    db: Session = Depends(get_db)
):
    """Reward user for downloading book"""
    service = PointsService(db)
    success = await service.reward_download(user_id, book_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reward points")
    return {"message": "Points rewarded successfully"}


@router.post("/user/{user_id}/reward/review/{book_id}")
async def reward_review(
    user_id: int,
    book_id: int,
    db: Session = Depends(get_db)
):
    """Reward user for writing review"""
    service = PointsService(db)
    success = await service.reward_review(user_id, book_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reward points")
    return {"message": "Points rewarded successfully"}


@router.post("/user/{user_id}/reward/rating/{book_id}")
async def reward_rating(
    user_id: int,
    book_id: int,
    db: Session = Depends(get_db)
):
    """Reward user for rating book"""
    service = PointsService(db)
    success = await service.reward_rating(user_id, book_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reward points")
    return {"message": "Points rewarded successfully"}
