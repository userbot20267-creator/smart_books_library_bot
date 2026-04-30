"""User API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserSchema, UserUpdateSchema, UserProfileSchema

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/telegram/{telegram_id}", response_model=UserSchema)
async def get_user_by_telegram_id(telegram_id: str, db: Session = Depends(get_db)):
    """Get user by telegram ID"""
    service = UserService(db)
    user = await service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/profile", response_model=UserProfileSchema)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile"""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    update_data: UserUpdateSchema,
    db: Session = Depends(get_db)
):
    """Update user information"""
    service = UserService(db)
    user = await service.update_user(user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/ban")
async def ban_user(user_id: int, reason: str = "", db: Session = Depends(get_db)):
    """Ban user"""
    service = UserService(db)
    success = await service.ban_user(user_id, reason)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User banned successfully"}


@router.post("/{user_id}/unban")
async def unban_user(user_id: int, db: Session = Depends(get_db)):
    """Unban user"""
    service = UserService(db)
    success = await service.unban_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User unbanned successfully"}
