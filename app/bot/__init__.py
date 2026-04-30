"""Bot package"""

from .handlers import router as old_handlers_router
from .handlers_features import router as new_features_router
from .keyboards import get_main_keyboard, get_category_keyboard

# دمج الراوترات: الجديد أولاً ليأخذ الأولوية
combined_router = Router()
combined_router.include_router(new_features_router)
combined_router.include_router(old_handlers_router)

__all__ = [
    "handlers_router",
    "get_main_keyboard",
    "get_category_keyboard",
]

# يُستخدم هذا المتغير في main.py
handlers_router = combined_router
