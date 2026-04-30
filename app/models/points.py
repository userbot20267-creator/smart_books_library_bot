"""Points and Transactions Models"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    DOWNLOAD = "download"
    REFERRAL = "referral"
    REVIEW = "review"
    RATING = "rating"
    COUPON = "coupon"
    PURCHASE = "purchase"
    ADMIN_BONUS = "admin_bonus"
    ADMIN_DEDUCT = "admin_deduct"


class UserPoints(Base):
    """User points model"""
    __tablename__ = "user_points"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    total_points = Column(Integer, default=0)
    available_points = Column(Integer, default=0)
    used_points = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="points")
    transactions = relationship("PointsTransaction", back_populates="user_points")

    def __repr__(self):
        return f"<UserPoints(user_id={self.user_id}, total={self.total_points})>"

    def add_points(self, amount: int) -> None:
        """Add points to user"""
        self.total_points += amount
        self.available_points += amount
        self.updated_at = datetime.utcnow()

    def deduct_points(self, amount: int) -> bool:
        """Deduct points from user, returns True if successful"""
        if self.available_points >= amount:
            self.available_points -= amount
            self.used_points += amount
            self.updated_at = datetime.utcnow()
            return True
        return False


class PointsTransaction(Base):
    """Points transaction history model"""
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_points.id"), nullable=False, index=True)
    
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(String(255), nullable=True)  # Book ID, Coupon ID, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user_points = relationship("UserPoints", back_populates="transactions")

    def __repr__(self):
        return f"<PointsTransaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"
