"""Coupon Models"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class CouponType(str, enum.Enum):
    """Coupon type enumeration"""
    POINTS = "points"
    DISCOUNT = "discount"
    PREMIUM_ACCESS = "premium_access"
    FREE_DOWNLOAD = "free_download"


class Coupon(Base):
    """Coupon model"""
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    coupon_type = Column(Enum(CouponType), nullable=False)
    
    # Value
    value = Column(Integer, nullable=False)  # Points or discount percentage
    
    # Validity
    max_uses = Column(Integer, nullable=True)  # None = unlimited
    current_uses = Column(Integer, default=0)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    description = Column(String(500), nullable=True)
    created_by = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_coupons = relationship("UserCoupon", back_populates="coupon", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Coupon(code={self.code}, type={self.coupon_type})>"

    def is_valid(self) -> bool:
        """Check if coupon is valid"""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses is not None and self.current_uses >= self.max_uses:
            return False
        return True

    def use(self) -> bool:
        """Use coupon, returns True if successful"""
        if self.is_valid():
            self.current_uses += 1
            self.updated_at = datetime.utcnow()
            return True
        return False


class UserCoupon(Base):
    """User coupon usage model"""
    __tablename__ = "user_coupons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, index=True)
    
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="coupons")
    coupon = relationship("Coupon", back_populates="user_coupons")

    def __repr__(self):
        return f"<UserCoupon(user_id={self.user_id}, coupon_id={self.coupon_id})>"
