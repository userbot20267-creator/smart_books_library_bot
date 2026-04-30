"""API package"""

from .books import router as books_router
from .users import router as users_router
from .search import router as search_router
from .reviews import router as reviews_router
from .points import router as points_router

__all__ = [
    "books_router",
    "users_router",
    "search_router",
    "reviews_router",
    "points_router",
]
