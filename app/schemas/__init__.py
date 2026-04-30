"""Schemas package"""

from .user import UserSchema, UserCreateSchema, UserUpdateSchema
from .book import BookSchema, BookCreateSchema, BookUpdateSchema, CategorySchema
from .review import ReviewSchema, ReviewCreateSchema, RatingSchema, RatingCreateSchema
from .points import UserPointsSchema, PointsTransactionSchema

__all__ = [
    "UserSchema",
    "UserCreateSchema",
    "UserUpdateSchema",
    "BookSchema",
    "BookCreateSchema",
    "BookUpdateSchema",
    "CategorySchema",
    "ReviewSchema",
    "ReviewCreateSchema",
    "RatingSchema",
    "RatingCreateSchema",
    "UserPointsSchema",
    "PointsTransactionSchema",
]
