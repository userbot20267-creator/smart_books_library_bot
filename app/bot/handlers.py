"""Telegram Bot Handlers Module"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, User as TelegramUser
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from app.bot.keyboards import get_main_keyboard, get_category_keyboard, get_settings_keyboard
from app.database import get_db_context
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    try:
        user = message.from_user
        
        # Get or create user in database
        with get_db_context() as db:
            user_service = UserService(db)
            await user_service.get_or_create_user(
                str(user.id),
                {
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            )
        
        welcome_text = f"""
🎉 أهلاً وسهلاً {user.first_name or 'صديقي'}!

مرحباً بك في 📚 مكتبة الكتب الذكية!

هنا يمكنك:
✨ تصفح آلاف الكتب المميزة
🔍 البحث عن الكتب بطرق متقدمة
⭐ تقييم الكتب وكتابة التعليقات
🎁 جمع النقاط والمكافآت
👥 مشاركة الكتب مع الأصدقاء

اختر من القائمة أدناه للبدء:
        """
        
        await message.answer(welcome_text, reply_markup=get_main_keyboard())
        
    except Exception as e:
        logger.error(f"Error in cmd_start: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")


@router.message(F.text == "📚 تصفح الكتب")
async def browse_books(message: Message):
    """Handle browse books"""
    try:
        await message.answer(
            "اختر القسم الذي تريد تصفحه:",
            reply_markup=get_category_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in browse_books: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")


@router.message(F.text == "🔍 بحث")
async def search_books(message: Message, state: FSMContext):
    """Handle search books"""
    try:
        await message.answer("اكتب كلمة البحث:")
        await state.set_state("searching")
    except Exception as e:
        logger.error(f"Error in search_books: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")


@router.message(F.text == "👤 ملفي الشخصي")
async def show_profile(message: Message):
    """Handle show profile"""
    try:
        user = message.from_user
        
        with get_db_context() as db:
            user_service = UserService(db)
            db_user = await user_service.get_user_by_telegram_id(str(user.id))
            
            if db_user:
                profile_text = f"""
👤 ملفك الشخصي:

الاسم: {db_user.get_full_name()}
المستوى: {db_user.level}
التحميلات: {db_user.total_downloads}
الكتب المقروءة: {db_user.total_books_read}
الحالة: {'🟢 مشترك' if db_user.is_premium else '⚪ عضو عادي'}
                """
                await message.answer(profile_text)
            else:
                await message.answer("لم نتمكن من العثور على بيانات ملفك الشخصي.")
    except Exception as e:
        logger.error(f"Error in show_profile: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")


@router.message(F.text == "🎁 نقاطي")
async def show_points(message: Message):
    """Handle show points"""
    try:
        user = message.from_user
        
        with get_db_context() as db:
            from app.services.points_service import PointsService
            user_service = UserService(db)
            db_user = await user_service.get_user_by_telegram_id(str(user.id))
            
            if db_user:
                points_service = PointsService(db)
                user_points = await points_service.get_user_points(db_user.id)
                
                if user_points:
                    points_text = f"""
🎁 نقاطك:

إجمالي النقاط: {user_points.total_points} 🏆
النقاط المتاحة: {user_points.available_points} ✨
النقاط المستخدمة: {user_points.used_points} 📊
                    """
                    await message.answer(points_text)
                else:
                    await message.answer("لم نتمكن من العثور على نقاطك.")
            else:
                await message.answer("لم نتمكن من العثور على بيانات حسابك.")
    except Exception as e:
        logger.error(f"Error in show_points: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")


@router.message(F.text == "⚙️ الإعدادات")
async def show_settings(message: Message):
    """Handle show settings"""
    try:
        await message.answer(
            "الإعدادات:",
            reply_markup=get_settings_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in show_settings: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")


@router.message(F.text == "🔙 عودة")
async def go_back(message: Message):
    """Handle go back"""
    try:
        await message.answer(
            "العودة إلى القائمة الرئيسية:",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in go_back: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    try:
        help_text = """
📚 مساعدة - مكتبة الكتب الذكية

الأوامر المتاحة:
/start - بدء التطبيق
/help - عرض المساعدة
/profile - عرض ملفك الشخصي
/points - عرض نقاطك
/search - البحث عن كتاب
/trending - الكتب الرائجة
/featured - الكتب المميزة

للمزيد من المساعدة، تواصل معنا عبر البريد الإلكتروني.
        """
        await message.answer(help_text)
    except Exception as e:
        logger.error(f"Error in cmd_help: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")


@router.callback_query(F.data.startswith("cat_"))
async def handle_category(callback: CallbackQuery):
    """Handle category selection"""
    try:
        category = callback.data.replace("cat_", "")
        await callback.message.answer(f"جاري تحميل كتب قسم {category}...")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_category: {str(e)}")
        await callback.answer("حدث خطأ")


@router.callback_query(F.data == "back")
async def handle_back(callback: CallbackQuery):
    """Handle back button"""
    try:
        await callback.message.answer(
            "العودة إلى القائمة الرئيسية:",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_back: {str(e)}")
        await callback.answer("حدث خطأ")
