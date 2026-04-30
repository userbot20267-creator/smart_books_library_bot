"""Points Service Module - Handles points and rewards operations"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.points import UserPoints, PointsTransaction, TransactionType
from app.models.user import User

logger = logging.getLogger(__name__)

# Points configuration
POINTS_CONFIG = {
    "download": 10,
    "review": 50,
    "rating": 20,
    "referral": 100,
    "coupon_bonus": 50,
}


class PointsService:
    """Service for points and rewards operations"""

    def __init__(self, db: Session):
        """Initialize points service"""
        self.db = db

    async def get_user_points(self, user_id: int) -> Optional[UserPoints]:
        """
        Get user points
        
        Args:
            user_id: User ID
            
        Returns:
            UserPoints object or None
        """
        try:
            user_points = self.db.query(UserPoints).filter(
                UserPoints.user_id == user_id
            ).first()
            return user_points

        except Exception as e:
            logger.error(f"Error getting user points: {str(e)}")
            return None

    async def add_points(
        self,
        user_id: int,
        amount: int,
        transaction_type: TransactionType,
        reference_id: str = None,
        description: str = None
    ) -> bool:
        """
        Add points to user
        
        Args:
            user_id: User ID
            amount: Points amount
            transaction_type: Type of transaction
            reference_id: Reference ID (book ID, coupon ID, etc.)
            description: Transaction description
            
        Returns:
            True if successful
        """
        try:
            user_points = await self.get_user_points(user_id)
            if not user_points:
                logger.warning(f"User points not found for user {user_id}")
                return False

            # Add points
            user_points.add_points(amount)

            # Create transaction record
            transaction = PointsTransaction(
                user_id=user_points.id,
                transaction_type=transaction_type,
                amount=amount,
                reference_id=reference_id,
                description=description
            )
            self.db.add(transaction)
            self.db.commit()

            logger.info(f"Added {amount} points to user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding points: {str(e)}")
            self.db.rollback()
            return False

    async def deduct_points(
        self,
        user_id: int,
        amount: int,
        transaction_type: TransactionType,
        reference_id: str = None,
        description: str = None
    ) -> bool:
        """
        Deduct points from user
        
        Args:
            user_id: User ID
            amount: Points amount
            transaction_type: Type of transaction
            reference_id: Reference ID
            description: Transaction description
            
        Returns:
            True if successful
        """
        try:
            user_points = await self.get_user_points(user_id)
            if not user_points:
                logger.warning(f"User points not found for user {user_id}")
                return False

            # Check if user has enough points
            if not user_points.deduct_points(amount):
                logger.warning(f"Insufficient points for user {user_id}")
                return False

            # Create transaction record
            transaction = PointsTransaction(
                user_id=user_points.id,
                transaction_type=transaction_type,
                amount=-amount,
                reference_id=reference_id,
                description=description
            )
            self.db.add(transaction)
            self.db.commit()

            logger.info(f"Deducted {amount} points from user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deducting points: {str(e)}")
            self.db.rollback()
            return False

    async def reward_download(self, user_id: int, book_id: int) -> bool:
        """
        Reward user for downloading book
        
        Args:
            user_id: User ID
            book_id: Book ID
            
        Returns:
            True if successful
        """
        return await self.add_points(
            user_id,
            POINTS_CONFIG["download"],
            TransactionType.DOWNLOAD,
            reference_id=str(book_id),
            description=f"Download reward for book {book_id}"
        )

    async def reward_review(self, user_id: int, book_id: int) -> bool:
        """
        Reward user for writing review
        
        Args:
            user_id: User ID
            book_id: Book ID
            
        Returns:
            True if successful
        """
        return await self.add_points(
            user_id,
            POINTS_CONFIG["review"],
            TransactionType.REVIEW,
            reference_id=str(book_id),
            description=f"Review reward for book {book_id}"
        )

    async def reward_rating(self, user_id: int, book_id: int) -> bool:
        """
        Reward user for rating book
        
        Args:
            user_id: User ID
            book_id: Book ID
            
        Returns:
            True if successful
        """
        return await self.add_points(
            user_id,
            POINTS_CONFIG["rating"],
            TransactionType.RATING,
            reference_id=str(book_id),
            description=f"Rating reward for book {book_id}"
        )

    async def reward_referral(self, referrer_id: int, referred_id: int) -> bool:
        """
        Reward referrer for successful referral
        
        Args:
            referrer_id: Referrer user ID
            referred_id: Referred user ID
            
        Returns:
            True if successful
        """
        return await self.add_points(
            referrer_id,
            POINTS_CONFIG["referral"],
            TransactionType.REFERRAL,
            reference_id=str(referred_id),
            description=f"Referral reward for user {referred_id}"
        )

    async def get_transaction_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list:
        """
        Get user transaction history
        
        Args:
            user_id: User ID
            limit: Number of transactions
            offset: Offset for pagination
            
        Returns:
            List of transactions
        """
        try:
            user_points = await self.get_user_points(user_id)
            if not user_points:
                return []

            transactions = self.db.query(PointsTransaction).filter(
                PointsTransaction.user_id == user_points.id
            ).order_by(PointsTransaction.created_at.desc()).limit(limit).offset(offset).all()

            return transactions

        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            return []

    async def get_leaderboard(self, limit: int = 10) -> list:
        """
        Get points leaderboard
        
        Args:
            limit: Number of users
            
        Returns:
            List of top users by points
        """
        try:
            leaderboard = self.db.query(UserPoints).order_by(
                UserPoints.total_points.desc()
            ).limit(limit).all()

            return leaderboard

        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return []
