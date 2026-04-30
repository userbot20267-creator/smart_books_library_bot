"""Admin Models"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class AdminRole(str, enum.Enum):
    """Admin role enumeration"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    CONTENT_MANAGER = "content_manager"


class AdminUser(Base):
    """Admin user model"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=True)
    
    # Role and permissions
    role = Column(Enum(AdminRole), default=AdminRole.MODERATOR)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    logs = relationship("AdminLog", back_populates="admin")

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username={self.username}, role={self.role})>"

    def is_super_admin(self) -> bool:
        """Check if user is super admin"""
        return self.role == AdminRole.SUPER_ADMIN

    def can_manage_content(self) -> bool:
        """Check if user can manage content"""
        return self.role in [AdminRole.SUPER_ADMIN, AdminRole.ADMIN, AdminRole.CONTENT_MANAGER]

    def can_manage_users(self) -> bool:
        """Check if user can manage users"""
        return self.role in [AdminRole.SUPER_ADMIN, AdminRole.ADMIN]

    def can_manage_admins(self) -> bool:
        """Check if user can manage other admins"""
        return self.role == AdminRole.SUPER_ADMIN


class AdminLog(Base):
    """Admin action log model"""
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    action = Column(String(255), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # create, update, delete, ban, etc.
    target_type = Column(String(50), nullable=False)  # user, book, coupon, etc.
    target_id = Column(String(255), nullable=True)
    
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    admin = relationship("AdminUser", back_populates="logs")
    user = relationship("User", back_populates="admin_logs")

    def __repr__(self):
        return f"<AdminLog(id={self.id}, action={self.action}, admin_id={self.admin_id})>"
