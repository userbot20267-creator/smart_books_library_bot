"""Bot package"""
from aiogram import Router  # ← أضف هذا السطر

from .handlers import router as old_handlers_router
from .handlers_features import router as new_features_router
from .keyboards import get_main_keyboard, get_category_keyboard

# دمج الراوترات
combined_router = Router()
combined_router.include_router(new_features_router)
combined_router.include_router(old_handlers_router)

handlers_router = combined_router

__all__ = [
    "handlers_router",
    "get_main_keyboard",
    "get_category_keyboard",
]
