"""
New Features Handlers – Search, Profile, Points, Trending, Featured, Categories fix
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config.settings import settings
from app.bot.keyboards import get_main_keyboard, get_category_keyboard, get_settings_keyboard
from app.database import get_db_context
from app.services.user_service import UserService
from app.services.points_service import PointsService
from app.services.book_service import BookService
from app.services.search_service import SearchService
from app.models.book import Book, BookCategory, BookStatus

logger = logging.getLogger(__name__)
router = Router()

# ---------- FSM states ----------
class SearchStates(StatesGroup):
    waiting_for_query = State()
    choosing_search_type = State()

# ---------- دوال مساعدة ----------

async def show_profile_logic(message: Message):
    """المنطق المشترك لعرض الملف الشخصي"""
    try:
        user = message.from_user
        with get_db_context() as db:
            user_service = UserService(db)
            db_user = await user_service.get_user_by_telegram_id(str(user.id))
            if db_user:
                text = (
                    f"👤 ملفك الشخصي:\n\n"
                    f"الاسم: {db_user.get_full_name()}\n"
                    f"المستوى: {db_user.level}\n"
                    f"التحميلات: {db_user.total_downloads}\n"
                    f"الكتب المقروءة: {db_user.total_books_read}\n"
                    f"الحالة: {'🟢 مشترك' if db_user.is_premium else '⚪ عضو عادي'}"
                )
                await message.answer(text)
            else:
                await message.answer("لم نتمكن من العثور على بيانات ملفك الشخصي.")
    except Exception as e:
        logger.error(f"Error showing profile: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")

async def show_points_logic(message: Message):
    """المنطق المشترك لعرض النقاط"""
    try:
        user = message.from_user
        with get_db_context() as db:
            user_service = UserService(db)
            db_user = await user_service.get_user_by_telegram_id(str(user.id))
            if db_user:
                points_service = PointsService(db)
                user_points = await points_service.get_user_points(db_user.id)
                if user_points:
                    text = (
                        f"🎁 نقاطك:\n\n"
                        f"إجمالي النقاط: {user_points.total_points} 🏆\n"
                        f"النقاط المتاحة: {user_points.available_points} ✨\n"
                        f"النقاط المستخدمة: {user_points.used_points} 📊"
                    )
                    await message.answer(text)
                else:
                    await message.answer("لم نتمكن من العثور على نقاطك.")
            else:
                await message.answer("لم نتمكن من العثور على بيانات حسابك.")
    except Exception as e:
        logger.error(f"Error showing points: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")

# ---------- الأوامر المفقودة ----------

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    await show_profile_logic(message)

@router.message(Command("points"))
async def cmd_points(message: Message):
    await show_points_logic(message)

@router.message(Command("trending"))
async def cmd_trending(message: Message):
    with get_db_context() as db:
        book_service = BookService(db)
        books = await book_service.get_trending_books(5)
        if books:
            text = "🔥 **الكتب الرائجة**\n\n"
            for i, book in enumerate(books, 1):
                text += f"{i}. {book.title} - {book.author}\n"
            await message.answer(text)
        else:
            await message.answer("لا توجد كتب رائجة حالياً.")

@router.message(Command("featured"))
async def cmd_featured(message: Message):
    with get_db_context() as db:
        book_service = BookService(db)
        books = await book_service.get_featured_books(5)
        if books:
            text = "⭐ **الكتب المميزة**\n\n"
            for i, book in enumerate(books, 1):
                text += f"{i}. {book.title} - {book.author}\n"
            await message.answer(text)
        else:
            await message.answer("لا توجد كتب مميزة حالياً.")

# ---------- البحث (داخلي وخارجي) ----------

@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    await message.answer("اكتب كلمة البحث (عنوان أو مؤلف):")
    await state.set_state(SearchStates.waiting_for_query)

# زر "🔍 بحث" – سيُلغى المعالج القديم تلقائياً لأن هذا الراوتر يُضم أولاً
@router.message(F.text == "🔍 بحث")
async def search_button(message: Message, state: FSMContext):
    await message.answer("اكتب كلمة البحث (عنوان أو مؤلف):")
    await state.set_state(SearchStates.waiting_for_query)

@router.message(SearchStates.waiting_for_query)
async def process_query(message: Message, state: FSMContext):
    query = message.text.strip()
    if not query:
        await message.answer("يرجى كتابة كلمة بحث صحيحة.")
        return
    await state.update_data(query=query)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 بحث نصي", callback_data="search_text")],
        [InlineKeyboardButton(text="🧠 بحث دلالي (AI)", callback_data="search_semantic")],
        [InlineKeyboardButton(text="🔙 إلغاء", callback_data="search_cancel")]
    ])
    await message.answer("اختر نوع البحث:", reply_markup=keyboard)
    await state.set_state(SearchStates.choosing_search_type)

@router.callback_query(SearchStates.choosing_search_type, F.data.startswith("search_"))
async def perform_search(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    query = data.get("query", "")
    search_type = callback.data

    if search_type == "search_cancel":
        await callback.message.answer("تم إلغاء البحث.")
        await callback.answer()
        await state.clear()
        return

    with get_db_context() as db:
        search_service = SearchService(db)
        if search_type == "search_text":
            books = await search_service.text_search(query, limit=5)
        else:  # semantic
            books = await search_service.semantic_search(query, limit=5)

    if books:
        text = f"📚 **نتائج البحث عن '{query}'**\n\n"
        for i, book in enumerate(books, 1):
            text += f"{i}. {book.title} - {book.author}\n"
        text += "\nلتحميل كتاب، أرسل /get متبوعاً برقم الكتاب"
        await callback.message.answer(text)
    else:
        await callback.message.answer("🔍 لم يتم العثور على كتب تطابق بحثك.")

    await callback.answer()
    await state.clear()

# ---------- تصفح الأقسام (تجاوز القديم) ----------

@router.message(F.text == "📚 تصفح الكتب")
async def browse_books(message: Message):
    await message.answer("اختر القسم الذي تريد تصفحه:", reply_markup=get_category_keyboard())

@router.callback_query(F.data.startswith("cat_"))
async def handle_category(callback: CallbackQuery):
    try:
        mapping = {
            "programming": "البرمجة",
            "self_dev": "التنمية الذاتية",
            "romance": "الرومانسية",
            "scifi": "الخيال العلمي",
            "history": "التاريخ"
        }
        cat_key = callback.data.replace("cat_", "")
        cat_name_ar = mapping.get(cat_key, cat_key)

        with get_db_context() as db:
            category = db.query(BookCategory).filter(BookCategory.name_ar == cat_name_ar).first()
            if not category:
                await callback.message.answer("القسم غير موجود حالياً.")
                await callback.answer()
                return

            books = db.query(Book).filter(
                Book.category_id == category.id,
                Book.status == BookStatus.ACTIVE
            ).order_by(Book.created_at.desc()).limit(10).all()

            if books:
                text = f"📚 **كتب قسم {cat_name_ar}**\n\n"
                for i, book in enumerate(books, 1):
                    text += f"{i}. {book.title} - {book.author}\n"
                text += "\nلتحميل كتاب، أرسل /get متبوعاً برقم الكتاب"
                await callback.message.answer(text)
            else:
                await callback.message.answer(f"لا توجد كتب في قسم {cat_name_ar} حالياً.")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_category: {str(e)}")
        await callback.answer("حدث خطأ، حاول لاحقاً.")

@router.callback_query(F.data == "back")
async def handle_back(callback: CallbackQuery):
    try:
        await callback.message.answer("العودة إلى القائمة الرئيسية:", reply_markup=get_main_keyboard())
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_back: {str(e)}")
        await callback.answer("حدث خطأ")

# ---------- الملف الشخصي و النقاط عبر الأزرار (نفس المنطق) ----------
@router.message(F.text == "👤 ملفي الشخصي")
async def button_profile(message: Message):
    await show_profile_logic(message)

@router.message(F.text == "🎁 نقاطي")
async def button_points(message: Message):
    await show_points_logic(message)
