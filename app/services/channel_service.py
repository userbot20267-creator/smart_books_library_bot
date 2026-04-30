"""Channel Service Module - Force join management"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.force_join import ForceJoinChannel

logger = logging.getLogger(__name__)

class ChannelService:
    def __init__(self, db: Session):
        self.db = db

    async def add_channel(self, channel_id: str, channel_name: str = None, required: bool = True) -> Optional[ForceJoinChannel]:
        """Add a channel to force join list"""
        try:
            channel = ForceJoinChannel(
                channel_id=channel_id,
                channel_name=channel_name,
                is_required=required
            )
            self.db.add(channel)
            self.db.commit()
            self.db.refresh(channel)
            return channel
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            self.db.rollback()
            return None

    async def remove_channel(self, channel_id: str) -> bool:
        """Remove a channel from list"""
        channel = self.db.query(ForceJoinChannel).filter_by(channel_id=channel_id).first()
        if channel:
            self.db.delete(channel)
            self.db.commit()
            return True
        return False

    async def get_all_channels(self) -> List[ForceJoinChannel]:
        """Get all force join channels"""
        return self.db.query(ForceJoinChannel).all()

    async def check_subscription(self, bot, user_id: int) -> tuple:
        """
        Check if user is subscribed to all required channels.
        Returns (is_subscribed: bool, missing_channel: ForceJoinChannel or None)
        """
        channels = self.db.query(ForceJoinChannel).filter_by(is_required=True).all()
        for channel in channels:
            try:
                member = await bot.get_chat_member(chat_id=channel.channel_id, user_id=user_id)
                if member.status in ['left', 'kicked']:
                    return False, channel
            except Exception as e:
                logger.error(f"Error checking {channel.channel_id}: {e}")
                continue
        return True, None
