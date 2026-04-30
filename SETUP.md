# 🔧 دليل الإعداد التفصيلي

## المتطلبات الأساسية

- Python 3.10 أو أحدث
- PostgreSQL 12 أو أحدث
- Redis 6 أو أحدث
- Docker و Docker Compose (اختياري)

## الخطوة 1: إعداد البيئة

### 1.1 استنساخ المستودع
```bash
git clone <repository-url>
cd smart_books_library_bot
```

### 1.2 إنشاء بيئة افتراضية
```bash
# على Linux/Mac
python3.10 -m venv venv
source venv/bin/activate

# على Windows
python -m venv venv
venv\Scripts\activate
```

### 1.3 تحديث pip
```bash
pip install --upgrade pip setuptools wheel
```

## الخطوة 2: تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

## الخطوة 3: إعداد قاعدة البيانات

### الخيار A: استخدام Docker Compose (موصى به)

```bash
# تشغيل جميع الخدمات
docker-compose up -d

# التحقق من حالة الخدمات
docker-compose ps

# عرض السجلات
docker-compose logs -f
```

### الخيار B: التثبيت اليدوي

#### تثبيت PostgreSQL

**على Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**على macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**على Windows:**
- حمّل من https://www.postgresql.org/download/windows/
- اتبع معالج التثبيت

#### إنشاء قاعدة البيانات

```bash
# الاتصال بـ PostgreSQL
psql -U postgres

# إنشاء المستخدم
CREATE USER smart_books WITH PASSWORD 'smart_books_password';

# إنشاء قاعدة البيانات
CREATE DATABASE smart_books_library OWNER smart_books;

# تثبيت pgvector
CREATE EXTENSION IF NOT EXISTS vector;

# الخروج
\q
```

#### تثبيت Redis

**على Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**على macOS:**
```bash
brew install redis
brew services start redis
```

**على Windows:**
- استخدم WSL أو Docker
- أو حمّل من https://github.com/microsoftarchive/redis/releases

## الخطوة 4: إعداد متغيرات البيئة

```bash
# نسخ ملف المثال
cp .env.example .env

# تعديل الملف بمحرر نصي
nano .env  # أو استخدم محررك المفضل
```

### متغيرات البيئة المهمة:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_ADMIN_ID=your_telegram_user_id

# Database
DATABASE_URL=postgresql://smart_books:smart_books_password@localhost:5432/smart_books_library
DATABASE_ECHO=False

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=True

# AI/LLM
OPENAI_API_KEY=your_openai_api_key
AI_MODEL=gpt-3.5-turbo

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=generate_a_random_key_here
ALGORITHM=HS256

# Application
DEBUG=True
LOG_LEVEL=INFO
```

### الحصول على Telegram Bot Token:

1. تحدث مع [@BotFather](https://t.me/botfather) على Telegram
2. أرسل `/newbot`
3. اتبع التعليمات
4. انسخ الـ Token

## الخطوة 5: تهيئة قاعدة البيانات

```bash
# تشغيل البرنامج لأول مرة سيقوم بإنشاء الجداول تلقائياً
python main.py
```

أو يمكنك تشغيل سكريبت التهيئة:

```bash
python -c "from app.database import init_db; init_db()"
```

## الخطوة 6: التحقق من التثبيت

```bash
# اختبار الاتصال بقاعدة البيانات
python -c "from app.database import engine; print(engine.connect())"

# اختبار الاتصال بـ Redis
python -c "import redis; r = redis.Redis(); print(r.ping())"
```

## الخطوة 7: تشغيل التطبيق

### تشغيل FastAPI Backend

```bash
python main.py
```

سيكون متاحاً على: `http://localhost:8000`

### تشغيل Telegram Bot (في terminal منفصل)

```bash
python bot_main.py
```

### الوصول إلى التوثيق التفاعلي

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## استكشاف الأخطاء

### خطأ: "Connection refused" لقاعدة البيانات

```bash
# تحقق من حالة PostgreSQL
sudo systemctl status postgresql

# أو إذا كنت تستخدم Docker
docker-compose logs postgres
```

### خطأ: "Invalid token" للـ Bot

- تأكد من نسخ الـ Token بشكل صحيح من BotFather
- تأكد من أن الـ Token في ملف .env بدون مسافات

### خطأ: "Module not found"

```bash
# تأكد من تثبيت جميع المتطلبات
pip install -r requirements.txt

# أو أعد تثبيتها
pip install --force-reinstall -r requirements.txt
```

## التطوير والاختبار

### تشغيل الاختبارات

```bash
# تثبيت متطلبات الاختبار
pip install pytest pytest-cov

# تشغيل الاختبارات
pytest

# مع تقرير التغطية
pytest --cov=app
```

### تشغيل Linter

```bash
# تثبيت
pip install flake8 black

# فحص الأخطاء
flake8 app/

# تنسيق الكود
black app/
```

## الخطوات التالية

1. اقرأ [دليل API](docs/api_guide.md)
2. اقرأ [دليل التطوير](docs/development_guide.md)
3. ابدأ بإضافة ميزات جديدة
4. ساهم في المشروع على GitHub

## الدعم

إذا واجهت أي مشاكل:

1. تحقق من السجلات في `logs/` directory
2. ابحث عن الخطأ في [GitHub Issues](https://github.com/your-repo/issues)
3. أنشئ issue جديدة مع وصف المشكلة والخطوات لإعادة إنتاجها

---

**ملاحظة:** تأكد من أن جميع الخدمات (PostgreSQL, Redis) تعمل قبل تشغيل التطبيق.
