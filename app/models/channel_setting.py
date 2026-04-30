from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class ChannelSetting(Base):
    __tablename__ = "channel_settings"
    id = Column(Integer, primary_key=True)
    channel_id = Column(String(100), nullable=False)  # @username
    auto_post = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
