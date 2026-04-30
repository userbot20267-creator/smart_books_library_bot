"""Models package"""

from .user import User
from .book import Book, BookCategory
from .review import Review, Rating
from .points import UserPoints, PointsTransaction
from .coupon import Coupon, UserCoupon
from .referral import Referral
from .author import Author
# وفي __all__ أضف "Author"
from .pack import Pack, PackBook
from .admin import AdminUser, AdminLog
from .force_join import ForceJoinChannel
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
    "Pack",
    "PackBook",
    "AdminUser",
    "AdminLog",


# أضفها إلى قائمة __all__
__all__ = [
    # ... الموجودين
    "ForceJoinChannel",
]
