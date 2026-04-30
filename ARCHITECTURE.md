# 🏗️ معمارية النظام

## نظرة عامة

تم تصميم مشروع مكتبة الكتب الذكية باستخدام معمارية **Modular** و **Microservices** لضمان سهولة التطوير والتوسع والصيانة.

## مكونات النظام الرئيسية

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Users                            │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌────────▼──────────┐
│  Telegram Bot    │    │   FastAPI Backend │
│  (aiogram 3.x)   │    │   (REST API)      │
└───────┬──────────┘    └────────┬──────────┘
        │                        │
        └────────────┬───────────┘
                     │
        ┌────────────▼────────────┐
        │   Application Layer     │
        │  ┌──────────────────┐   │
        │  │ Services Layer   │   │
        │  │ ┌──────────────┐ │   │
        │  │ │ AI Service   │ │   │
        │  │ │ Search Svc   │ │   │
        │  │ │ User Svc     │ │   │
        │  │ │ Book Svc     │ │   │
        │  │ │ Points Svc   │ │   │
        │  │ │ Admin Svc    │ │   │
        │  │ └──────────────┘ │   │
        │  └──────────────────┘   │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Data Access Layer     │
        │  ┌──────────────────┐   │
        │  │ SQLAlchemy ORM   │   │
        │  │ Models & Schemas │   │
        │  └──────────────────┘   │
        └────────────┬────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────────┐  ┌───▼────────┐  ┌───▼────────┐
│ PostgreSQL │  │   Redis    │  │  pgvector  │
│            │  │  (Cache)   │  │ (Embeddings)
└────────────┘  └────────────┘  └────────────┘
```

## طبقات التطبيق

### 1. طبقة العرض (Presentation Layer)

#### Telegram Bot (aiogram)
- معالجات الرسائل والأوامر
- واجهات المستخدم (Keyboards)
- إدارة الحالة (FSM)

#### FastAPI Backend
- نقاط نهاية REST API
- توثيق تفاعلي (Swagger, ReDoc)
- معالجة الأخطاء

### 2. طبقة التطبيق (Application Layer)

#### Services
- **AIService**: معالجة الذكاء الاصطناعي
- **SearchService**: البحث المتقدم
- **UserService**: إدارة المستخدمين
- **BookService**: إدارة الكتب
- **PointsService**: إدارة النقاط
- **AdminService**: عمليات الإدارة

### 3. طبقة الوصول للبيانات (Data Access Layer)

#### Models
- User
- Book, BookCategory
- Review, Rating
- UserPoints, PointsTransaction
- Coupon, UserCoupon
- Referral
- Pack, PackBook
- AdminUser, AdminLog

#### Schemas (Pydantic)
- تحقق من صحة البيانات
- توثيق API
- تسلسل/فك تسلسل البيانات

### 4. طبقة قاعدة البيانات (Database Layer)

- PostgreSQL: تخزين البيانات الأساسية
- pgvector: تخزين المتجهات (Embeddings)
- Redis: التخزين المؤقت والجلسات

## تدفق البيانات

### سيناريو: تحميل كتاب

```
1. المستخدم يرسل أمر التحميل عبر Telegram
   ↓
2. Bot Handler يستقبل الأمر
   ↓
3. Bot يستدعي API endpoint
   ↓
4. FastAPI يستقبل الطلب
   ↓
5. BookService يعالج الطلب
   ↓
6. يتم تحديث قاعدة البيانات
   ↓
7. PointsService يضيف النقاط
   ↓
8. الرد يُرسل للمستخدم
```

### سيناريو: البحث الدلالي

```
1. المستخدم يبحث عن "البرمجة"
   ↓
2. SearchService يستقبل الاستعلام
   ↓
3. AIService ينشئ embeddings للاستعلام
   ↓
4. البحث في pgvector عن أقرب embeddings
   ↓
5. ترتيب النتائج حسب التشابه
   ↓
6. إرجاع النتائج للمستخدم
```

## معايير التصميم

### Separation of Concerns (فصل المسؤوليات)
- كل service مسؤول عن مجال واحد فقط
- كل model يمثل كيان واحد فقط
- كل API endpoint له وظيفة محددة

### DRY (Don't Repeat Yourself)
- إعادة استخدام الكود
- دوال مساعدة مشتركة
- نماذج قابلة للتوسع

### SOLID Principles
- Single Responsibility
- Open/Closed Principle
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

## الأمان

### Authentication
- JWT Tokens للـ API
- Telegram User ID للـ Bot

### Authorization
- Role-based Access Control (RBAC)
- Admin roles: Super Admin, Admin, Moderator, Content Manager

### Data Protection
- تشفير كلمات المرور (bcrypt)
- HTTPS في الإنتاج
- SQL Injection Prevention (SQLAlchemy ORM)

## الأداء

### Caching
- Redis للبيانات المتكررة
- Cache tags للتحديثات الذكية

### Database Optimization
- Indexes على الأعمدة المهمة
- Connection pooling
- Query optimization

### Async Processing
- Async/await للعمليات الطويلة
- Background tasks مع Celery (اختياري)

## التوسعية

### إضافة ميزة جديدة

1. **إنشاء Model** (إن لزم الأمر)
   ```python
   # app/models/new_feature.py
   class NewFeature(Base):
       __tablename__ = "new_features"
       # ...
   ```

2. **إنشاء Schema** (للـ API)
   ```python
   # app/schemas/new_feature.py
   class NewFeatureSchema(BaseModel):
       # ...
   ```

3. **إنشاء Service**
   ```python
   # app/services/new_feature_service.py
   class NewFeatureService:
       # ...
   ```

4. **إنشاء API Endpoints**
   ```python
   # app/api/new_feature.py
   @router.get("/api/new-feature")
   async def get_new_feature():
       # ...
   ```

5. **إضافة Bot Handlers** (إن لزم الأمر)
   ```python
   # app/bot/handlers.py
   @router.message(F.text == "New Feature")
   async def handle_new_feature():
       # ...
   ```

## الاختبار

### Unit Tests
```bash
pytest tests/test_services.py
```

### Integration Tests
```bash
pytest tests/test_api.py
```

### End-to-End Tests
```bash
pytest tests/test_e2e.py
```

## النشر

### Development
```bash
python main.py
python bot_main.py
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## المراقبة والتسجيل

### Logging
- Console logging للتطوير
- File logging للإنتاج
- Separate error logs

### Monitoring
- Health check endpoints
- Database connection monitoring
- API response time tracking

## المستقبل

### Planned Improvements
- [ ] Microservices architecture
- [ ] Message queue (RabbitMQ)
- [ ] Distributed caching
- [ ] GraphQL API
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Machine learning recommendations

---

**ملاحظة:** هذه المعمارية قابلة للتطور والتحسين حسب احتياجات المشروع.
