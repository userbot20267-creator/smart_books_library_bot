"""Book and BookCategory Models"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class BookStatus(str, enum.Enum):
    """Book status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    PENDING = "pending"
    REJECTED = "rejected"


class BookCategory(Base):
    """Book category model"""
    __tablename__ = "book_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    name_ar = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)
    parent_id = Column(Integer, ForeignKey("book_categories.id"), nullable=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    books = relationship("Book", back_populates="category")
    subcategories = relationship("BookCategory", remote_side=[id])

    def __repr__(self):
        return f"<BookCategory(id={self.id}, name={self.name})>"


class Book(Base):
    """Book model for storing book information"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("book_categories.id"), nullable=True)
    
    # File information
    file_path = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    file_type = Column(String(20), default="pdf")  # pdf, epub, txt
    
    # Book details
    isbn = Column(String(20), unique=True, nullable=True, index=True)
    publisher = Column(String(255), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    pages = Column(Integer, nullable=True)
    language = Column(String(10), default="ar")
    
    # Cover and metadata
    cover_image_url = Column(String(500), nullable=True)
    cover_image_path = Column(String(500), nullable=True)
    
    # AI-generated content
    ai_summary = Column(Text, nullable=True)
    ai_tags = Column(String(500), nullable=True)
    ai_classification = Column(String(255), nullable=True)
    embedding_vector = Column(String(10000), nullable=True)  # Stored as JSON string
    
    # Statistics
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    
    # Status and management
    status = Column(Enum(BookStatus), default=BookStatus.ACTIVE, index=True)
    is_featured = Column(Boolean, default=False)
    is_exclusive = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uploaded_by = Column(String(50), nullable=True)  # Admin user ID

    # Relationships
    category = relationship("BookCategory", back_populates="books")
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="book", cascade="all, delete-orphan")
    packs = relationship("PackBook", back_populates="book")

    def __repr__(self):
        return f"<Book(id={self.id}, title={self.title}, author={self.author})>"

    def get_display_name(self) -> str:
        """Get book display name"""
        return f"{self.title} - {self.author}"

    def is_available(self) -> bool:
        """Check if book is available for download"""
        return self.status == BookStatus.ACTIVE and self.file_path is not None
