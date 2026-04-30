"""Referral Model"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Referral(Base):
    """Referral model for tracking user referrals"""
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Referral code
    referral_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    reward_given = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    reward_date = Column(DateTime, nullable=True)

    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_given")
    referred = relationship("User", foreign_keys=[referred_id], back_populates="referrals_received")

    def __repr__(self):
        return f"<Referral(referrer_id={self.referrer_id}, referred_id={self.referred_id})>"
