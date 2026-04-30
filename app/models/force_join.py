"""Force Join Channel Model"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class ForceJoinChannel(Base):
    """Model for forced join channels"""
    __tablename__ = "force_join_channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(100), unique=True, nullable=False, index=True)  # @channel_username
    channel_name = Column(String(255), nullable=True)
    is_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ForceJoinChannel(channel_id='{self.channel_id}', required={self.is_required})>"
