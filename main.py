"""
Main FastAPI Application Module
Entry point for the Smart Books Library Bot Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from config.settings import settings
from app.database import init_db
from app.api import books_router, users_router, search_router, reviews_router, points_router
from app.utils.logger import setup_logger

# استيراد مكونات aiogram
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from app.bot import handlers_router  # الراوتر من البوت

import asyncio

# Setup logger
logger = setup_logger()

# -------------------- دورة حياة التطبيق --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting Smart Books Library Bot Backend")
    
    # تهيئة قاعدة البيانات
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    # تشغيل بوت تيليجرام (aiogram)
    if settings.TELEGRAM_BOT_TOKEN:
        try:
            # إعداد البوت والـ dispatcher
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            dp = Dispatcher(storage=MemoryStorage())
            dp.include_router(handlers_router)  # تضمين الراوتر من البوت

            # تعيين أوامر القائمة (اختياري)
            await bot.set_my_commands([
                BotCommand(command="start", description="بدء الاستخدام"),
                BotCommand(command="help", description="المساعدة"),
            ])

            # بدء polling كمهمة خلفية
            polling_task = asyncio.create_task(dp.start_polling(bot))
            logger.info("Telegram Bot started successfully")
            
            # تخزين الكائنات في app.state لاستخدامها لاحقاً
            app.state.bot = bot
            app.state.dp = dp
            app.state.polling_task = polling_task
        except Exception as e:
            logger.error(f"Failed to start Telegram Bot: {str(e)}")
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot will not start")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Books Library Bot Backend")
    if hasattr(app.state, 'bot'):
        try:
            # إيقاف polling وإغلاق الجلسة
            if hasattr(app.state, 'polling_task'):
                app.state.polling_task.cancel()
            await app.state.bot.session.close()
            await app.state.bot.delete_webhook(drop_pending_updates=True)
            logger.info("Telegram Bot stopped")
        except Exception:
            pass

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Smart Books Library Bot",
    description="API for Smart Books Library Bot on Telegram",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(books_router)
app.include_router(users_router)
app.include_router(search_router)
app.include_router(reviews_router)
app.include_router(points_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Smart Books Library Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Smart Books Library Bot",
        "version": "1.0.0"
    }

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.debug else "An error occurred"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_reload,
        log_level=settings.log_level.lower()
    )
