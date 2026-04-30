"""
New Features Handlers – Search, Profile, Points, Trending, Featured, Categories fix,
Force Join Channels, Owner Interactive Panel, Categories & Authors Management,
AI-Powered Book Finder & Adder
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
from app.services.category_service import CategoryService
from app.services.author_service import AuthorService
from app.services.ai_service import AIService
from app.models.book import Book, BookCategory, BookStatus
from app.models.author import Author
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

class CategoryStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_name_ar = State()
    waiting_for_category_id = State()

class AuthorStates(StatesGroup):
    waiting_for_author_name = State()
    waiting_for_author_bio = State()
    waiting_for_author_id = State()

class AIFindStates(StatesGroup):
    waiting_for_description = State()
    choosing_category = State()
    choosing_author = State()
    waiting_for_new_author = State()

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

        if is_owner(event.from_user.id):
            return await handler(event, data)

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

# ---------- أوامر الاشتراك الإجباري ----------
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

# ---------- إدارة الأقسام ----------
@router.message(Command("addcategory"))
async def cmd_addcategory(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    await message.answer("أرسل اسم القسم (عربي أو إنجليزي):")
    await state.set_state(CategoryStates.waiting_for_category_name)

@router.message(CategoryStates.waiting_for_category_name)
async def process_cat_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("أرسل الاسم العربي للقسم (أو ارسل 'تخطي'):")
    await state.set_state(CategoryStates.waiting_for_category_name_ar)

@router.message(CategoryStates.waiting_for_category_name_ar)
async def process_cat_name_ar(message: Message, state: FSMContext):
    name_ar = message.text.strip()
    if name_ar == 'تخطي':
        name_ar = None
    data = await state.get_data()
    with get_db_context() as db:
        service = CategoryService(db)
        cat = await service.create(name=data['name'], name_ar=name_ar)
        if cat:
            await message.answer(f"✅ تم إنشاء القسم '{cat.name}'")
        else:
            await message.answer("❌ فشل في إنشاء القسم")
    await state.clear()

@router.message(Command("deletecategory"))
async def cmd_deletecategory(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    await message.answer("أرسل ID القسم الذي تريد حذفه:")
    await state.set_state(CategoryStates.waiting_for_category_id)

@router.message(CategoryStates.waiting_for_category_id)
async def process_delete_category(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("يجب إرسال رقم صحيح")
    cat_id = int(message.text)
    with get_db_context() as db:
        service = CategoryService(db)
        if await service.delete(cat_id):
            await message.answer("✅ تم الحذف")
        else:
            await message.answer("❌ القسم غير موجود")
    await state.clear()

@router.message(Command("listcategories"))
async def cmd_listcategories(message: Message):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    with get_db_context() as db:
        cats = await CategoryService(db).list_all()
        if not cats:
            return await message.answer("لا توجد أقسام")
        text = "📁 **الأقسام**\n\n"
        for c in cats:
            text += f"• {c.name} (ID: {c.id})\n"
        await message.answer(text)

# ---------- إدارة المؤلفين ----------
@router.message(Command("addauthor"))
async def cmd_addauthor(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    await message.answer("أرسل اسم المؤلف:")
    await state.set_state(AuthorStates.waiting_for_author_name)

@router.message(AuthorStates.waiting_for_author_name)
async def process_author_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("أرسل نبذة عن المؤلف (أو 'تخطي'):")
    await state.set_state(AuthorStates.waiting_for_author_bio)

@router.message(AuthorStates.waiting_for_author_bio)
async def process_author_bio(message: Message, state: FSMContext):
    bio = message.text.strip()
    if bio == 'تخطي':
        bio = None
    data = await state.get_data()
    with get_db_context() as db:
        service = AuthorService(db)
        author = await service.create(name=data['name'], bio=bio)
        await message.answer(f"✅ تم إضافة المؤلف '{author.name}'")
    await state.clear()

@router.message(Command("deleteauthor"))
async def cmd_deleteauthor(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    await message.answer("أرسل ID المؤلف:")
    await state.set_state(AuthorStates.waiting_for_author_id)

@router.message(AuthorStates.waiting_for_author_id)
async def process_delete_author(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("يجب أن يكون رقماً")
    author_id = int(message.text)
    with get_db_context() as db:
        if await AuthorService(db).delete(author_id):
            await message.answer("✅ تم حذف المؤلف")
        else:
            await message.answer("❌ المؤلف غير موجود")
    await state.clear()

@router.message(Command("listauthors"))
async def cmd_listauthors(message: Message):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    with get_db_context() as db:
        authors = await AuthorService(db).list_all()
        if not authors:
            return await message.answer("لا يوجد مؤلفون")
        text = "✍️ **المؤلفون**\n\n"
        for a in authors:
            text += f"• {a.name} (ID: {a.id})\n"
        await message.answer(text)

# ---------- أمر الذكاء الاصطناعي: /aifind ----------
@router.message(Command("aifind"))
async def cmd_aifind(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ غير مصرح")
    await message.answer("اكتب وصفًا للكتاب الذي تريد البحث عنه (مثلاً: 'كتاب عن تعلم الآلة بالعربية'):")
    await state.set_state(AIFindStates.waiting_for_description)

@router.message(AIFindStates.waiting_for_description)
async def process_ai_description(message: Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await message.answer("جاري البحث بواسطة الذكاء الاصطناعي...")
    ai_service = AIService()
    # محاكاة رد من AI (يمكنك استبدالها بدالة حقيقية مثل generate_summary أو API call)
    suggested = await ai_service.classify_book(
        title="عنوان مقترح",
        description=message.text.strip(),
        author="مؤلف مقترح"
    )
    if not suggested:
        await message.answer("فشل الاتصال بالذكاء الاصطناعي. تأكد من المفاتيح أو حاول لاحقًا.")
        await state.clear()
        return
    
    # تخزين بيانات الكتاب المقترحة
    await state.update_data(
        book_title="عنوان مقترح من AI",
        book_author="مؤلف مقترح من AI",
        book_desc=message.text.strip()
    )
    
    text = (
        f"🤖 **اقتراح الكتاب**\n\n"
        f"📖 العنوان: {suggested.get('title', 'غير معروف')}\n"
        f"✍️ المؤلف: {suggested.get('author', 'غير معروف')}\n"
        f"📝 التصنيف: {suggested.get('category', 'غير معروف')}\n"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ إضافة فعليًا", callback_data="aifind_confirm")],
        [InlineKeyboardButton(text="❌ تجاهل", callback_data="aifind_cancel")]
    ])
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(AIFindStates.choosing_category)

@router.callback_query(AIFindStates.choosing_category, F.data == "aifind_confirm")
async def aifind_choose_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    # عرض الأقسام المتاحة
    with get_db_context() as db:
        cats = await CategoryService(db).list_all()
        if not cats:
            await callback.message.answer("لا توجد أقسام. قم بإنشاء قسم أولاً.")
            return
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=c.name, callback_data=f"aicat_{c.id}")] for c in cats
        ])
    await callback.message.answer("اختر قسمًا للكتاب:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("aicat_"))
async def aifind_set_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.replace("aicat_", ""))
    await state.update_data(cat_id=cat_id)
    # عرض المؤلفين
    with get_db_context() as db:
        authors = await AuthorService(db).list_all()
        if not authors:
            # عدم وجود مؤلفين، يمكن اختيار إضافة جديد
            await callback.message.answer("لا يوجد مؤلفون في القاعدة. أرسل اسم المؤلف الجديد:")
            await state.set_state(AIFindStates.waiting_for_new_author)
            await callback.answer()
            return
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=a.name, callback_data=f"aiauth_{a.id}")] for a in authors
        ])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="إنشاء مؤلف جديد", callback_data="aiauth_new")])
    await callback.message.answer("اختر المؤلف:", reply_markup=keyboard)
    await state.set_state(AIFindStates.choosing_author)
    await callback.answer()

@router.callback_query(AIFindStates.choosing_author, F.data == "aiauth_new")
async def aifind_new_author(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("أرسل اسم المؤلف الجديد:")
    await state.set_state(AIFindStates.waiting_for_new_author)
    await callback.answer()

@router.message(AIFindStates.waiting_for_new_author)
async def process_new_author(message: Message, state: FSMContext):
    name = message.text.strip()
    with get_db_context() as db:
        author = await AuthorService(db).create(name=name)
        await state.update_data(author_id=author.id)
    # الموافقة على إضافة الكتاب
    data = await state.get_data()
    with get_db_context() as db:
        book = Book(
            title=data.get('book_title', 'عنوان AI'),
            author=author.name,
            description=data.get('book_desc', ''),
            category_id=data.get('cat_id'),
            file_path=None,
            status=BookStatus.PENDING
        )
        db.add(book)
        db.commit()
        await message.answer(f"✅ تمت إضافة الكتاب '{book.title}' تحت القسم المختار والمؤلف '{author.name}'.")
    await state.clear()

@router.callback_query(AIFindStates.choosing_author, F.data.startswith("aiauth_"))
async def aifind_existing_author(callback: CallbackQuery, state: FSMContext):
    author_id = int(callback.data.replace("aiauth_", ""))
    await state.update_data(author_id=author_id)
    with get_db_context() as db:
        author = db.query(Author).get(author_id)
        if not author:
            await callback.message.answer("المؤلف غير موجود.")
            await state.clear()
            return
        data = await state.get_data()
        book = Book(
            title=data.get('book_title', 'عنوان AI'),
            author=author.name,
            description=data.get('book_desc', ''),
            category_id=data.get('cat_id'),
            file_path=None,
            status=BookStatus.PENDING
        )
        db.add(book)
        db.commit()
        await callback.message.answer(f"✅ تمت إضافة الكتاب '{book.title}' تحت القسم المختار والمؤلف '{author.name}'.")
    await state.clear()

@router.callback_query(F.data == "aifind_cancel")
async def aifind_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("تم إلغاء العملية.")
    await state.clear()
    await callback.answer()

# ---------- لوحة تحكم المالك التفاعلية ----------
@router.message(Command("admin"))
async def cmd_admin_panel(message: Message):
    if not is_owner(message.from_user.id):
        return await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 إحصائيات", callback_data="owner_stats")],
        [InlineKeyboardButton(text="📚 كتب قيد المراجعة", callback_data="owner_pending")],
        [InlineKeyboardButton(text="📡 قنوات الإجبار", callback_data="owner_channels")],
        [InlineKeyboardButton(text="📁 إدارة الأقسام", callback_data="owner_categories")],
        [InlineKeyboardButton(text="✍️ إدارة المؤلفين", callback_data="owner_authors")],
        [InlineKeyboardButton(text="🤖 بحث ذكي / AI", callback_data="owner_aifind")],
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

@router.callback_query(F.data == "owner_categories")
async def owner_categories(callback: CallbackQuery):
    await cmd_listcategories(callback.message)
    await callback.answer()

@router.callback_query(F.data == "owner_authors")
async def owner_authors(callback: CallbackQuery):
    await cmd_listauthors(callback.message)
    await callback.answer()

@router.callback_query(F.data == "owner_aifind")
async def owner_aifind(callback: CallbackQuery):
    await cmd_aifind(callback.message, AIFindStates.waiting_for_description)
    await callback.answer()

@router.callback_query(F.data == "owner_close")
async def owner_close(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
