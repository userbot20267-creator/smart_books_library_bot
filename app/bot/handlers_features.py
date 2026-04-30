"""
New Features Handlers – Search, Profile, Points, Trending, Featured, Categories fix,
Force Join Channels, Owner Interactive Panel
"""

import logging
from aiogram import Router, F, BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from typing import Any, Awaitable, Callable, Dict

from config.settings import settings
from app.bot.keyboards import (
    get_main_keyboard,
    get_category_keyboard,
    get_settings_keyboard,
    get_commands_inline_keyboard
)
from app.database import get_db_context
from app.services.user_service import UserService
from app.services.points_service import PointsService
from app.services.book_service import BookService
from app.services.search_service import SearchService
from app.services.channel_service import ChannelService
from app.models.book import Book, BookCategory, BookStatus
from app.admin.admin_service import AdminService

logger = logging.getLogger(__name__)
router = Router()

# ---------- FSM states ----------
class SearchStates(StatesGroup):
    waiting_for_query = State()
    choosing_search_type = State()

class ChannelStates(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_channel_remove = State()

# ---------- دوال مساعدة ----------
def is_owner(telegram_id: int) -> bool:
    return telegram_id == settings.telegram_admin_id

async def show_profile_logic(message: Message):
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

# ---------- Middleware الاشتراك الإجباري ----------
class ForceJoinMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)

        # تخطي الفحص للمالك
        if is_owner(event.from_user.id):
            return await handler(event, data)

        # تخطي أمر /start
        if event.text and event.text.startswith('/start'):
            return await handler(event, data)

        bot = data['bot']
        with get_db_context() as db:
            service = ChannelService(db)
            is_sub, missing = await service.check_subscription(bot, event.from_user.id)
            if not is_sub and missing:
                await event.answer(
                    f"⚠️ يجب الاشتراك في القناة التالية أولاً:\n{missing.channel_id}\n\n"
                    "اشترك ثم أعد المحاولة."
                )
                return

        return await handler(event, data)

router.message.middleware(ForceJoinMiddleware())
router.callback_query.middleware(ForceJoinMiddleware())

# ---------- الأوامر الأساسية ----------
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

# ---------- البحث ----------
@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    await message.answer("اكتب كلمة البحث (عنوان أو مؤلف):")
    await state.set_state(SearchStates.waiting_for_query)

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
        else:
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

# ---------- تصفح الأقسام ----------
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

# ---------- أزرار الملف الشخصي والنقاط ----------
@router.message(F.text == "👤 ملفي الشخصي")
async def button_profile(message: Message):
    await show_profile_logic(message)

@router.message(F.text == "🎁 نقاطي")
async def button_points(message: Message):
    await show_points_logic(message)

# ---------- لوحة الأوامر التفاعلية ----------
@router.callback_query(F.data == "cmd_profile")
async def inline_profile(callback: CallbackQuery):
    await show_profile_logic(callback.message)
    await callback.answer()

@router.callback_query(F.data == "cmd_points")
async def inline_points(callback: CallbackQuery):
    await show_points_logic(callback.message)
    await callback.answer()

@router.callback_query(F.data == "cmd_trending")
async def inline_trending(callback: CallbackQuery):
    with get_db_context() as db:
        book_service = BookService(db)
        books = await book_service.get_trending_books(5)
        if books:
            text = "🔥 **الكتب الرائجة**\n\n"
            for i, book in enumerate(books, 1):
                text += f"{i}. {book.title} - {book.author}\n"
            await callback.message.answer(text)
        else:
            await callback.message.answer("لا توجد كتب رائجة حالياً.")
    await callback.answer()

@router.callback_query(F.data == "cmd_featured")
async def inline_featured(callback: CallbackQuery):
    with get_db_context() as db:
        book_service = BookService(db)
        books = await book_service.get_featured_books(5)
        if books:
            text = "⭐ **الكتب المميزة**\n\n"
            for i, book in enumerate(books, 1):
                text += f"{i}. {book.title} - {book.author}\n"
            await callback.message.answer(text)
        else:
            await callback.message.answer("لا توجد كتب مميزة حالياً.")
    await callback.answer()

@router.callback_query(F.data == "cmd_search")
async def inline_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("اكتب كلمة البحث (عنوان أو مؤلف):")
    await state.set_state(SearchStates.waiting_for_query)
    await callback.answer()

@router.callback_query(F.data == "cmd_help")
async def inline_help(callback: CallbackQuery):
    help_text = (
        "📚 **مساعدة - مكتبة الكتب الذكية**\n\n"
        "الأوامر المتاحة:\n"
        "/start - بدء التطبيق\n"
        "/help - عرض المساعدة\n"
        "👤 ملفي الشخصي - معلوماتك\n"
        "🎁 نقاطي - مجموع نقاطك\n"
        "🔥 الكتب الرائجة - الأكثر تحميلاً\n"
        "⭐ الكتب المميزة - المختارة يدوياً\n"
        "🔍 بحث - ابحث عن أي كتاب\n"
        "📚 تصفح الكتب - تصفح الأقسام"
    )
    await callback.message.answer(help_text)
    await callback.answer()

@router.message(Command("commands"))
@router.message(F.text == "📋 الأوامر")
async def show_commands(message: Message):
    await message.answer("اختر الأمر الذي تريد:", reply_markup=get_commands_inline_keyboard())

# ---------- أوامر الاشتراك الإجباري (للمالك فقط) ----------
@router.message(Command("addchannel"))
async def cmd_add_channel(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    await message.answer("📡 أرسل معرف القناة (مثال: @MyChannel):")
    await state.set_state(ChannelStates.waiting_for_channel_id)

@router.message(ChannelStates.waiting_for_channel_id)
async def process_channel_id(message: Message, state: FSMContext):
    channel_id = message.text.strip()
    if not channel_id.startswith("@"):
        return await message.answer("يجب أن يبدأ المعرف بـ @")
    with get_db_context() as db:
        service = ChannelService(db)
        success = await service.add_channel(channel_id)
        if success:
            await message.answer(f"✅ تمت إضافة القناة {channel_id} للاشتراك الإجباري")
        else:
            await message.answer("❌ فشلت الإضافة، قد تكون القناة مكررة")
    await state.clear()

@router.message(Command("removechannel"))
async def cmd_remove_channel(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    await message.answer("📡 أرسل معرف القناة التي تريد حذفها:")
    await state.set_state(ChannelStates.waiting_for_channel_remove)

@router.message(ChannelStates.waiting_for_channel_remove)
async def process_remove_channel(message: Message, state: FSMContext):
    channel_id = message.text.strip()
    with get_db_context() as db:
        service = ChannelService(db)
        if await service.remove_channel(channel_id):
            await message.answer(f"✅ تم حذف القناة {channel_id}")
        else:
            await message.answer("❌ القناة غير موجودة في القائمة")
    await state.clear()

@router.message(Command("listchannels"))
async def cmd_list_channels(message: Message):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    with get_db_context() as db:
        service = ChannelService(db)
        channels = await service.get_all_channels()
        if not channels:
            return await message.answer("لا توجد قنوات اشتراك إجباري حالياً")
        text = "📋 **قنوات الاشتراك الإجباري**\n\n"
        for ch in channels:
            text += f"• {ch.channel_id} {'✅ إجباري' if ch.is_required else '🟡 اختياري'}\n"
        await message.answer(text)

# ---------- لوحة تحكم المالك التفاعلية ----------
@router.message(Command("admin"))
async def cmd_admin_panel(message: Message):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 إحصائيات", callback_data="owner_stats")],
        [InlineKeyboardButton(text="📚 كتب قيد المراجعة", callback_data="owner_pending")],
        [InlineKeyboardButton(text="📡 قنوات الإجبار", callback_data="owner_channels")],
        [InlineKeyboardButton(text="🔙 إغلاق", callback_data="owner_close")]
    ])
    await message.answer("👑 **لوحة تحكم المالك**", reply_markup=keyboard)

@router.callback_query(F.data == "owner_stats")
async def owner_stats(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("غير مصرح", show_alert=True)
        return
    with get_db_context() as db:
        service = AdminService(db)
        stats = await service.get_statistics()
        text = (
            "📊 **إحصائيات النظام**\n\n"
            f"👥 المستخدمين: {stats.get('total_users', 0)}\n"
            f"🟢 نشط: {stats.get('active_users', 0)}\n"
            f"📚 الكتب: {stats.get('total_books', 0)}\n"
            f"📗 نشطة: {stats.get('active_books', 0)}\n"
            f"⏳ قيد المراجعة: {stats.get('pending_books', 0)}"
        )
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "owner_pending")
async def owner_pending(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("غير مصرح", show_alert=True)
        return
    with get_db_context() as db:
        service = AdminService(db)
        books = await service.get_pending_books(10)
        if books:
            text = "📚 **كتب قيد المراجعة**\n\n"
            for b in books:
                text += f"• {b.title} (ID: {b.id})\n"
        else:
            text = "لا توجد كتب قيد المراجعة."
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "owner_channels")
async def owner_channels(callback: CallbackQuery):
    await cmd_list_channels(callback.message)
    await callback.answer()

@router.callback_query(F.data == "owner_close")
async def owner_close(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
