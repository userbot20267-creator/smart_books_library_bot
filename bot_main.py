"""
Telegram Bot Main Module
Entry point for the aiogram Telegram Bot
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config.settings import settings
from app.utils.logger import setup_logger
from app.bot.handlers import router as handlers_router
from app.database import init_db

# Setup logger
logger = setup_logger()


async def main():
    """Main bot function"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        
        # Create bot and dispatcher
        bot = Bot(token=settings.telegram_bot_token)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Include routers
        dp.include_router(handlers_router)
        
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
