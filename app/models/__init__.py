"""Models package"""

from .user import User
from .book import Book, BookCategory
from .review import Review, Rating
from .points import UserPoints, PointsTransaction
from .coupon import Coupon, UserCoupon
from .referral import Referral
from .author import Author
from .pack import Pack, PackBook
from .admin import AdminUser, AdminLog
from .force_join import ForceJoinChannel
from .notification import NotificationSetting
from .channel_setting import ChannelSetting
# وفي __all__ أضف "NotificationSetting", "ChannelSetting"

__all__ = [
    "User",
    "Book",
    "BookCategory",
    "Review",
    "Rating",
    "UserPoints",
    "PointsTransaction",
    "Coupon",
    "UserCoupon",
    "Referral",
    "Author",
    "Pack",
    "PackBook",
    "AdminUser",
    "AdminLog",
    "ForceJoinChannel",
]
