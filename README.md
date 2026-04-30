# 📚 مكتبة الكتب الذكية - Smart Books Library Bot

نظام متطور لإدارة المكتبات الرقمية عبر تيليجرام، يجمع بين إدارة المحتوى التقليدية وتقنيات الذكاء الاصطناعي الحديثة.

## 🛠 المتطلبات التقنية

- **اللغة:** Python 3.10+
- **الإطار البرمجي:** aiogram 3.x (للبوت) و FastAPI (للـ Backend)
- **قاعدة البيانات:** PostgreSQL مع pgvector
- **الذكاء الاصطناعي:** OpenRouter API أو OpenAI API
- **البيئة:** Docker, Docker Compose

## 📦 المتطلبات والتثبيت

### 1. استنساخ المستودع
```bash
git clone <repository-url>
cd smart_books_library_bot
```

### 2. إنشاء بيئة افتراضية
```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate  # على Windows
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد متغيرات البيئة
```bash
cp .env.example .env
# ثم عدّل ملف .env بإضافة بيانات اعتمادك
```

### 5. إعداد قاعدة البيانات
```bash
# استخدام Docker Compose
docker-compose up -d

# أو إعداد يدوي
# تأكد من تثبيت PostgreSQL و Redis
```

## 🚀 البدء السريع

### تشغيل FastAPI Backend
```bash
python main.py
```

سيكون الـ API متاحاً على: `http://localhost:8000`

### تشغيل Telegram Bot
```bash
python bot_main.py
```

### الوصول إلى التوثيق التفاعلي
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📁 هيكل المشروع

```
smart_books_library_bot/
├── app/
│   ├── models/              # نماذج قاعدة البيانات
│   ├── services/            # خدمات الأعمال
│   ├── api/                 # نقاط نهاية FastAPI
│   ├── bot/                 # معالجات Telegram Bot
│   ├── admin/               # خدمات الإدارة
│   ├── schemas/             # Pydantic schemas
│   ├── utils/               # دوال مساعدة
│   └── database.py          # إعدادات قاعدة البيانات
├── config/
│   └── settings.py          # إعدادات التطبيق
├── migrations/              # ملفات الهجرة (Alembic)
├── tests/                   # اختبارات الوحدة
├── main.py                  # نقطة دخول FastAPI
├── bot_main.py              # نقطة دخول Telegram Bot
├── requirements.txt         # المتطلبات
├── docker-compose.yml       # إعدادات Docker
├── Dockerfile               # صورة Docker
└── README.md                # هذا الملف
```

## 🎯 الميزات الرئيسية

### للمستخدمين
- 📖 تصفح هرمي للكتب (أقسام ← مؤلفين ← كتب)
- 🔍 بحث متطور (نصي، دلالي، OCR)
- ⭐ نظام تقييم وتعليقات
- 🎁 نظام النقاط والمكافآت
- 👥 نظام الإحالة
- 📚 الباقات التعليمية المنظمة

### للمالك/الإدارة
- 📁 إدارة المحتوى المتقدمة
- 🤖 التصنيف الآلي للكتب
- 👥 إدارة المستخدمين
- 📊 التقارير والإحصائيات
- 🔐 إدارة الصلاحيات

## 🔌 نقاط نهاية API الرئيسية

### الكتب
- `GET /api/books/` - قائمة الكتب
- `GET /api/books/{book_id}` - تفاصيل الكتاب
- `GET /api/books/featured` - الكتب المميزة
- `GET /api/books/trending` - الكتب الرائجة

### البحث
- `GET /api/search/text` - بحث نصي
- `GET /api/search/semantic` - بحث دلالي
- `GET /api/search/advanced` - بحث متقدم

### المستخدمين
- `GET /api/users/{user_id}` - بيانات المستخدم
- `PUT /api/users/{user_id}` - تحديث البيانات
- `POST /api/users/{user_id}/ban` - حظر المستخدم

### النقاط
- `GET /api/points/user/{user_id}` - نقاط المستخدم
- `GET /api/points/leaderboard` - لوحة الصدارة
- `GET /api/points/user/{user_id}/history` - سجل المعاملات

## 🔐 الأمان

- تحديد معدل الطلبات (Rate Limiting)
- منع السبام
- فلترة المحتوى الضار
- تشفير كلمات المرور
- JWT Authentication

## 📝 متغيرات البيئة المهمة

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_ADMIN_ID=your_admin_id

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smart_books_library

# AI/LLM
OPENAI_API_KEY=your_key
AI_MODEL=gpt-3.5-turbo

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Security
SECRET_KEY=your_secret_key_change_in_production
```

## 🧪 الاختبار

```bash
# تشغيل الاختبارات
pytest

# مع تقرير التغطية
pytest --cov=app
```

## 📚 التوثيق الإضافية

- [نموذج قاعدة البيانات](docs/database_schema.md)
- [دليل API](docs/api_guide.md)
- [دليل التطوير](docs/development_guide.md)

## 🚀 النشر

### على Railway
```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# نشر المشروع
railway up
```

### على Heroku
```bash
# تثبيت Heroku CLI
# ثم
heroku login
heroku create your-app-name
git push heroku main
```

## 🤝 المساهمة

نرحب بالمساهمات! يرجى:

1. Fork المستودع
2. إنشاء فرع للميزة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت MIT License - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## 📞 التواصل والدعم

- البريد الإلكتروني: support@smartbookslibrary.com
- Telegram: @SmartBooksLibraryBot
- GitHub Issues: [Report a bug](https://github.com/your-repo/issues)

## 🙏 شكر خاص

شكراً لجميع المساهمين والمستخدمين الذين يدعمون هذا المشروع.

---

**ملاحظة:** هذا المشروع قيد التطوير المستمر. قد تتغير الميزات والتوثيق.
