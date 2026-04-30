"""Telegram Keyboards Module (Dynamic Categories)"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.database import SessionLocal
from app.models.book import BookCategory


def get_main_keyboard():
    """Get main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 تصفح الكتب"), KeyboardButton(text="🔍 بحث")],
            [KeyboardButton(text="⭐ تقييماتي"), KeyboardButton(text="👤 ملفي الشخصي")],
            [KeyboardButton(text="🎁 نقاطي"), KeyboardButton(text="⚙️ الإعدادات")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


async def get_category_keyboard():
    """Get dynamic category selection keyboard from database"""
    db = SessionLocal()
    try:
        categories = db.query(BookCategory).filter(BookCategory.is_active == True).all()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for cat in categories:
            label = cat.name_ar or cat.name
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=label, callback_data=f"cat_{cat.id}")]
            )
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="العودة", callback_data="back")])
        return keyboard
    finally:
        db.close()


def get_book_keyboard(book_id: int):
    """Get book action keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📥 تحميل", callback_data=f"download_{book_id}")],
            [InlineKeyboardButton(text="⭐ تقييم", callback_data=f"rate_{book_id}")],
            [InlineKeyboardButton(text="💬 تعليق", callback_data=f"review_{book_id}")],
            [InlineKeyboardButton(text="❤️ إعجاب", callback_data=f"like_{book_id}")],
            [InlineKeyboardButton(text="🔙 عودة", callback_data="back")],
        ]
    )
    return keyboard


def get_rating_keyboard(book_id: int):
    """Get rating selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐", callback_data=f"rate_1_{book_id}"),
                InlineKeyboardButton(text="⭐⭐", callback_data=f"rate_2_{book_id}"),
                InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"rate_3_{book_id}"),
            ],
            [
                InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"rate_4_{book_id}"),
                InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"rate_5_{book_id}"),
            ],
            [InlineKeyboardButton(text="🔙 إلغاء", callback_data="back")],
        ]
    )
    return keyboard


def get_settings_keyboard():
    """Get settings keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 اللغة"), KeyboardButton(text="🔔 الإشعارات")],
            [KeyboardButton(text="🔐 الخصوصية"), KeyboardButton(text="ℹ️ حول التطبيق")],
            [KeyboardButton(text="🔙 عودة")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def get_language_keyboard():
    """Get language selection keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="العربية 🇸🇦", callback_data="lang_ar")],
            [InlineKeyboardButton(text="English 🇺🇸", callback_data="lang_en")],
            [InlineKeyboardButton(text="🔙 عودة", callback_data="back")],
        ]
    )
    return keyboard


def get_commands_inline_keyboard():
    """لوحة الأوامر الرئيسية كأزرار Inline"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 ملفي الشخصي", callback_data="cmd_profile")],
            [InlineKeyboardButton(text="🎁 نقاطي", callback_data="cmd_points")],
            [InlineKeyboardButton(text="🔥 الكتب الرائجة", callback_data="cmd_trending")],
            [InlineKeyboardButton(text="⭐ الكتب المميزة", callback_data="cmd_featured")],
            [InlineKeyboardButton(text="🔍 بحث", callback_data="cmd_search")],
            [InlineKeyboardButton(text="📋 المساعدة", callback_data="cmd_help")],
        ]
    )
    return keyboard
