"""Admin Service Module - Handles admin operations"""

import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.admin import AdminUser, AdminLog, AdminRole
from app.models.book import Book, BookStatus
from app.models.user import User, UserStatus

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin operations"""

    def __init__(self, db: Session):
        """Initialize admin service"""
        self.db = db

    async def get_admin(self, admin_id: int) -> Optional[AdminUser]:
        """Get admin by ID"""
        try:
            admin = self.db.query(AdminUser).filter(AdminUser.id == admin_id).first()
            return admin
        except Exception as e:
            logger.error(f"Error getting admin: {str(e)}")
            return None

    async def get_admin_by_telegram_id(self, telegram_id: str) -> Optional[AdminUser]:
        """Get admin by telegram ID"""
        try:
            admin = self.db.query(AdminUser).filter(
                AdminUser.telegram_id == telegram_id
            ).first()
            return admin
        except Exception as e:
            logger.error(f"Error getting admin by telegram ID: {str(e)}")
            return None

    async def approve_book(self, book_id: int, admin_id: int) -> bool:
        """Approve pending book"""
        try:
            book = self.db.query(Book).filter(Book.id == book_id).first()
            if not book:
                return False

            book.status = BookStatus.ACTIVE
            
            # Log action
            await self.log_action(
                admin_id,
                "approve_book",
                "book",
                str(book_id),
                f"Approved book: {book.title}"
            )
            
            self.db.commit()
            logger.info(f"Approved book: {book_id}")
            return True

        except Exception as e:
            logger.error(f"Error approving book: {str(e)}")
            self.db.rollback()
            return False

    async def reject_book(self, book_id: int, admin_id: int, reason: str = "") -> bool:
        """Reject pending book"""
        try:
            book = self.db.query(Book).filter(Book.id == book_id).first()
            if not book:
                return False

            book.status = BookStatus.REJECTED
            
            # Log action
            await self.log_action(
                admin_id,
                "reject_book",
                "book",
                str(book_id),
                f"Rejected book: {book.title}. Reason: {reason}"
            )
            
            self.db.commit()
            logger.info(f"Rejected book: {book_id}")
            return True

        except Exception as e:
            logger.error(f"Error rejecting book: {str(e)}")
            self.db.rollback()
            return False

    async def delete_book(self, book_id: int, admin_id: int, reason: str = "") -> bool:
        """Delete book"""
        try:
            book = self.db.query(Book).filter(Book.id == book_id).first()
            if not book:
                return False

            # Log action
            await self.log_action(
                admin_id,
                "delete_book",
                "book",
                str(book_id),
                f"Deleted book: {book.title}. Reason: {reason}"
            )
            
            self.db.delete(book)
            self.db.commit()
            logger.info(f"Deleted book: {book_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting book: {str(e)}")
            self.db.rollback()
            return False

    async def ban_user(self, user_id: int, admin_id: int, reason: str = "") -> bool:
        """Ban user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.status = UserStatus.BANNED
            
            # Log action
            await self.log_action(
                admin_id,
                "ban_user",
                "user",
                str(user_id),
                f"Banned user: {user.get_full_name()}. Reason: {reason}"
            )
            
            self.db.commit()
            logger.info(f"Banned user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error banning user: {str(e)}")
            self.db.rollback()
            return False

    async def unban_user(self, user_id: int, admin_id: int) -> bool:
        """Unban user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            user.status = UserStatus.ACTIVE
            
            # Log action
            await self.log_action(
                admin_id,
                "unban_user",
                "user",
                str(user_id),
                f"Unbanned user: {user.get_full_name()}"
            )
            
            self.db.commit()
            logger.info(f"Unbanned user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error unbanning user: {str(e)}")
            self.db.rollback()
            return False

    async def log_action(
        self,
        admin_id: int,
        action: str,
        action_type: str,
        target_type: str,
        target_id: str,
        details: str = None,
        ip_address: str = None
    ) -> bool:
        """Log admin action"""
        try:
            log = AdminLog(
                admin_id=admin_id,
                action=action,
                action_type=action_type,
                target_type=target_type,
                target_id=target_id,
                details=details,
                ip_address=ip_address
            )
            self.db.add(log)
            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error logging action: {str(e)}")
            self.db.rollback()
            return False

    async def get_admin_logs(
        self,
        admin_id: int = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AdminLog]:
        """Get admin logs"""
        try:
            query = self.db.query(AdminLog)
            
            if admin_id:
                query = query.filter(AdminLog.admin_id == admin_id)
            
            logs = query.order_by(AdminLog.created_at.desc()).limit(limit).offset(offset).all()
            return logs

        except Exception as e:
            logger.error(f"Error getting admin logs: {str(e)}")
            return []

    async def get_pending_books(self, limit: int = 50) -> List[Book]:
        """Get pending books for approval"""
        try:
            books = self.db.query(Book).filter(
                Book.status == BookStatus.PENDING
            ).order_by(Book.created_at).limit(limit).all()
            return books

        except Exception as e:
            logger.error(f"Error getting pending books: {str(e)}")
            return []

    async def get_statistics(self) -> dict:
        """Get system statistics"""
        try:
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.status == UserStatus.ACTIVE).count()
            total_books = self.db.query(Book).count()
            active_books = self.db.query(Book).filter(Book.status == BookStatus.ACTIVE).count()
            pending_books = self.db.query(Book).filter(Book.status == BookStatus.PENDING).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_books": total_books,
                "active_books": active_books,
                "pending_books": pending_books,
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
