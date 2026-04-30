"""User Service Module - Handles user operations"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserStatus
from app.models.points import UserPoints
from app.schemas.user import UserCreateSchema, UserUpdateSchema

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations"""

    def __init__(self, db: Session):
        """Initialize user service"""
        self.db = db

    async def get_or_create_user(self, telegram_id: str, user_data: dict) -> User:
        """
        Get existing user or create new one
        
        Args:
            telegram_id: Telegram user ID
            user_data: User data dictionary
            
        Returns:
            User object
        """
        try:
            user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                # Create new user
                user = User(
                    telegram_id=telegram_id,
                    username=user_data.get("username"),
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                    language=user_data.get("language", "ar")
                )
                self.db.add(user)
                
                # Create user points
                user_points = UserPoints(user=user)
                self.db.add(user_points)
                
                self.db.commit()
                self.db.refresh(user)
                logger.info(f"Created new user: {telegram_id}")
            
            return user

        except Exception as e:
            logger.error(f"Error in get_or_create_user: {str(e)}")
            self.db.rollback()
            raise

    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            return user

        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None

    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """
        Get user by telegram ID
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User object or None
        """
        try:
            user = self.db.query(User).filter(User.telegram_id == telegram_id).first()
            return user

        except Exception as e:
            logger.error(f"Error getting user by telegram ID: {str(e)}")
            return None

    async def update_user(self, user_id: int, update_data: UserUpdateSchema) -> Optional[User]:
        """
        Update user information
        
        Args:
            user_id: User ID
            update_data: Update data
            
        Returns:
            Updated user object or None
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return None

            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(user, key, value)

            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Updated user: {user_id}")
            return user

        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            self.db.rollback()
            return None

    async def ban_user(self, user_id: int, reason: str = "") -> bool:
        """
        Ban user
        
        Args:
            user_id: User ID
            reason: Ban reason
            
        Returns:
            True if successful
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return False

            user.status = UserStatus.BANNED
            self.db.commit()
            logger.info(f"Banned user: {user_id}, reason: {reason}")
            return True

        except Exception as e:
            logger.error(f"Error banning user: {str(e)}")
            self.db.rollback()
            return False

    async def unban_user(self, user_id: int) -> bool:
        """
        Unban user
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return False

            user.status = UserStatus.ACTIVE
            self.db.commit()
            logger.info(f"Unbanned user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error unbanning user: {str(e)}")
            self.db.rollback()
            return False

    async def increment_download_count(self, user_id: int) -> bool:
        """
        Increment user download count
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return False

            user.total_downloads += 1
            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error incrementing download count: {str(e)}")
            self.db.rollback()
            return False

    async def update_level(self, user_id: int) -> bool:
        """
        Update user level based on activity
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            user = await self.get_user(user_id)
            if not user:
                return False

            # Calculate level based on downloads and books read
            total_activity = user.total_downloads + user.total_books_read
            new_level = (total_activity // 50) + 1
            
            if new_level != user.level:
                user.level = new_level
                self.db.commit()
                logger.info(f"Updated user level: {user_id} -> {new_level}")

            return True

        except Exception as e:
            logger.error(f"Error updating level: {str(e)}")
            self.db.rollback()
            return False
