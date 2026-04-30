"""Pack and PackBook Models"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Pack(Base):
    """Learning pack model - organized learning paths"""
    __tablename__ = "packs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    title_ar = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Metadata
    icon_url = Column(String(500), nullable=True)
    difficulty_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    estimated_hours = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Statistics
    enrolled_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    books = relationship("PackBook", back_populates="pack", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pack(id={self.id}, title={self.title})>"


class PackBook(Base):
    """Pack book association model"""
    __tablename__ = "pack_books"

    id = Column(Integer, primary_key=True, index=True)
    pack_id = Column(Integer, ForeignKey("packs.id"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    
    # Order in pack
    order = Column(Integer, default=0)
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pack = relationship("Pack", back_populates="books")
    book = relationship("Book", back_populates="packs")

    def __repr__(self):
        return f"<PackBook(pack_id={self.pack_id}, book_id={self.book_id})>"
