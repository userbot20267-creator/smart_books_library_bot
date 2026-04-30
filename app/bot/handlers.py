"""Telegram Bot Handlers Module – User & Owner Commands"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config.settings import settings
from app.bot.keyboards import (
    get_main_keyboard,
    get_category_keyboard,
    get_settings_keyboard
)
from app.database import get_db_context
from app.services.user_service import UserService
from app.services.points_service import PointsService
from app.admin.admin_service import AdminService
from app.models.book import Book, BookCategory, BookStatus  # ← أضيف

logger = logging.getLogger(__name__)
router = Router()

# ---------- حالات FSM لأوامر المالك ----------
class AdminStates(StatesGroup):
    waiting_for_user_id_to_ban = State()
    waiting_for_ban_reason = State()
    waiting_for_user_id_to_unban = State()
    waiting_for_book_id_to_approve = State()
    waiting_for_book_id_to_reject = State()

# ---------- فحص المالك ----------
def is_owner(telegram_id: int) -> bool:
    return telegram_id == settings.telegram_admin_id

# ========== الأوامر العامة ==========

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    try:
        user = message.from_user
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

        if is_owner(user.id):
            welcome_text = (
                f"👑 أهلاً بك يا مالك النظام {user.first_name or 'العزيز'}!\n\n"
                "📌 أوامر المالك المتاحة:\n"
                "/admin - لوحة تحكم المالك\n"
                "/stats - إحصائيات سريعة\n"
                "/pending - الكتب قيد المراجعة\n"
                "/ban - حظر مستخدم\n"
                "/unban - فك حظر مستخدم\n"
                "/approve - موافقة على كتاب\n"
                "/reject - رفض كتاب\n\n"
                "للمستخدمين العاديين:\n"
                "/start - بدء الاستخدام\n"
                "/help - المساعدة"
            )
        else:
            welcome_text = (
                f"🎉 أهلاً وسهلاً {user.first_name or 'صديقي'}!\n\n"
                "مرحباً بك في 📚 مكتبة الكتب الذكية!\n\n"
                "هنا يمكنك:\n"
                "✨ تصفح آلاف الكتب المميزة\n"
                "🔍 البحث عن الكتب بطرق متقدمة\n"
                "⭐ تقييم الكتب وكتابة التعليقات\n"
                "🎁 جمع النقاط والمكافآت\n"
                "👥 مشاركة الكتب مع الأصدقاء\n\n"
                "اختر من القائمة أدناه للبدء:"
            )

        await message.answer(welcome_text, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Error in cmd_start: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📚 مساعدة - مكتبة الكتب الذكية\n\n"
        "الأوامر المتاحة:\n"
        "/start - بدء التطبيق\n"
        "/help - عرض المساعدة\n"
        "/profile - عرض ملفك الشخصي\n"
        "/points - عرض نقاطك\n"
        "/search - البحث عن كتاب\n"
        "/trending - الكتب الرائجة\n"
        "/featured - الكتب المميزة"
    )
    await message.answer(help_text)

@router.message(F.text == "📚 تصفح الكتب")
async def browse_books(message: Message):
    await message.answer("اختر القسم الذي تريد تصفحه:", reply_markup=get_category_keyboard())

@router.message(F.text == "🔍 بحث")
async def search_books(message: Message, state: FSMContext):
    await message.answer("اكتب كلمة البحث:")
    await state.set_state("searching")

@router.message(F.text == "👤 ملفي الشخصي")
async def show_profile(message: Message):
    try:
        user = message.from_user
        with get_db_context() as db:
            user_service = UserService(db)
            db_user = await user_service.get_user_by_telegram_id(str(user.id))
            if db_user:
                profile_text = (
                    f"👤 ملفك الشخصي:\n\n"
                    f"الاسم: {db_user.get_full_name()}\n"
                    f"المستوى: {db_user.level}\n"
                    f"التحميلات: {db_user.total_downloads}\n"
                    f"الكتب المقروءة: {db_user.total_books_read}\n"
                    f"الحالة: {'🟢 مشترك' if db_user.is_premium else '⚪ عضو عادي'}"
                )
                await message.answer(profile_text)
            else:
                await message.answer("لم نتمكن من العثور على بيانات ملفك الشخصي.")
    except Exception as e:
        logger.error(f"Error in show_profile: {str(e)}")
        await message.answer("حدث خطأ. يرجى المحاولة لاحقاً.")

@router.message(F.text == "🎁 نقاطي")
async def show_points(message: Message):
    try:
        user = message.from_user
        with get_db_context() as db:
            user_service = UserService(db)
            db_user = await user_service.get_user_by_telegram_id(str(user.id))
            if db_user:
                points_service = PointsService(db)
                user_points = await points_service.get_user_points(db_user.id)
                if user_points:
                    points_text = (
                        f"🎁 نقاطك:\n\n"
                        f"إجمالي النقاط: {user_points.total_points} 🏆\n"
                        f"النقاط المتاحة: {user_points.available_points} ✨\n"
                        f"النقاط المستخدمة: {user_points.used_points} 📊"
                    )
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
    await message.answer("الإعدادات:", reply_markup=get_settings_keyboard())

@router.message(F.text == "🔙 عودة")
async def go_back(message: Message):
    await message.answer("العودة إلى القائمة الرئيسية:", reply_markup=get_main_keyboard())

# ========== أوامر المالك ==========

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
        return
    await message.answer(
        "👑 **لوحة تحكم المالك**\n\n"
        "📊 /stats - عرض إحصائيات النظام\n"
        "📚 /pending - الكتب بانتظار الموافقة\n"
        "🚫 /ban - حظر مستخدم\n"
        "✅ /unban - فك حظر مستخدم\n"
        "✅ /approve - الموافقة على كتاب\n"
        "❌ /reject - رفض كتاب"
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
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
        await message.answer(text)

@router.message(Command("pending"))
async def cmd_pending_books(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
        return
    with get_db_context() as db:
        service = AdminService(db)
        books = await service.get_pending_books(10)
        if not books:
            await message.answer("لا توجد كتب بانتظار المراجعة.")
            return
        text = "📚 **كتب قيد المراجعة**\n\n"
        for book in books:
            text += f"• {book.title} (ID: {book.id})\n"
        text += "\nللموافقة: /approve\nللرفض: /reject"
        await message.answer(text)

@router.message(Command("ban"))
async def cmd_ban_start(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
        return
    await message.answer("📍 أرسل ID المستخدم الذي تريد حظره:")
    await state.set_state(AdminStates.waiting_for_user_id_to_ban)

@router.message(AdminStates.waiting_for_user_id_to_ban)
async def process_ban_user_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ يجب إرسال رقم صحيح.")
        return
    user_id = int(message.text)
    await state.update_data(user_id=user_id)
    await message.answer("✏️ اكتب سبب الحظر (أو أرسل 'تخطي'):")
    await state.set_state(AdminStates.waiting_for_ban_reason)

@router.message(AdminStates.waiting_for_ban_reason)
async def process_ban_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    reason = message.text if message.text != 'تخطي' else ""
    with get_db_context() as db:
        service = AdminService(db)
        success = await service.ban_user(user_id, settings.telegram_admin_id, reason)
        if success:
            await message.answer(f"✅ تم حظر المستخدم {user_id}")
        else:
            await message.answer("❌ فشل حظر المستخدم. تأكد من صحة ID.")
    await state.clear()

@router.message(Command("unban"))
async def cmd_unban_start(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
        return
    await message.answer("📍 أرسل ID المستخدم لفك الحظر:")
    await state.set_state(AdminStates.waiting_for_user_id_to_unban)

@router.message(AdminStates.waiting_for_user_id_to_unban)
async def process_unban(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ يجب إرسال رقم صحيح.")
        return
    user_id = int(message.text)
    with get_db_context() as db:
        service = AdminService(db)
        success = await service.unban_user(user_id, settings.telegram_admin_id)
        if success:
            await message.answer(f"✅ تم فك حظر المستخدم {user_id}")
        else:
            await message.answer("❌ فشل فك الحظر. تأكد من صحة ID.")
    await state.clear()

@router.message(Command("approve"))
async def cmd_approve_start(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
        return
    await message.answer("📍 أرسل ID الكتاب للموافقة عليه:")
    await state.set_state(AdminStates.waiting_for_book_id_to_approve)

@router.message(AdminStates.waiting_for_book_id_to_approve)
async def process_approve(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ يجب إرسال رقم صحيح.")
        return
    book_id = int(message.text)
    with get_db_context() as db:
        service = AdminService(db)
        success = await service.approve_book(book_id, settings.telegram_admin_id)
        if success:
            await message.answer(f"✅ تمت الموافقة على الكتاب {book_id}")
        else:
            await message.answer("❌ فشلت الموافقة. تأكد من صحة ID.")
    await state.clear()

@router.message(Command("reject"))
async def cmd_reject_start(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        await message.answer("❌ هذا الأمر مخصص للمالك فقط.")
        return
    await message.answer("📍 أرسل ID الكتاب لرفضه:")
    await state.set_state(AdminStates.waiting_for_book_id_to_reject)

@router.message(AdminStates.waiting_for_book_id_to_reject)
async def process_reject(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ يجب إرسال رقم صحيح.")
        return
    book_id = int(message.text)
    with get_db_context() as db:
        service = AdminService(db)
        success = await service.reject_book(book_id, settings.telegram_admin_id, "مرفوض من المالك")
        if success:
            await message.answer(f"✅ تم رفض الكتاب {book_id}")
        else:
            await message.answer("❌ فشل الرفض. تأكد من صحة ID.")
    await state.clear()

# ========== معالجات الـ Callbacks ==========

@router.callback_query(F.data.startswith("cat_"))
async def handle_category(callback: CallbackQuery):
    """معالجة اختيار القسم وعرض الكتب الموجودة فيه"""
    try:
        # اسم القسم بالعربية كما هو في قاعدة البيانات
        category_data = {
            "programming": "البرمجة",
            "self_dev": "التنمية الذاتية",
            "romance": "الرومانسية",
            "scifi": "الخيال العلمي",
            "history": "التاريخ"
        }
        cat_key = callback.data.replace("cat_", "")
        cat_name_ar = category_data.get(cat_key, cat_key)

        with get_db_context() as db:
            # البحث عن القسم باستخدام الاسم العربي
            category = db.query(BookCategory).filter(BookCategory.name_ar == cat_name_ar).first()
            
            if not category:
                await callback.message.answer("القسم غير موجود حالياً.")
                await callback.answer()
                return

            # جلب آخر 10 كتب نشطة في هذا القسم
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
