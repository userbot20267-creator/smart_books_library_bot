"""Book Service Module - Handles book operations"""

import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.book import Book, BookStatus, BookCategory
from app.models.review import Review, Rating
from app.schemas.book import BookCreateSchema, BookUpdateSchema

logger = logging.getLogger(__name__)


class BookService:
    """Service for book operations"""

    def __init__(self, db: Session):
        """Initialize book service"""
        self.db = db

    async def get_book(self, book_id: int) -> Optional[Book]:
        """
        Get book by ID
        
        Args:
            book_id: Book ID
            
        Returns:
            Book object or None
        """
        try:
            book = self.db.query(Book).filter(Book.id == book_id).first()
            if book:
                book.view_count += 1
                self.db.commit()
            return book

        except Exception as e:
            logger.error(f"Error getting book: {str(e)}")
            return None

    async def create_book(self, book_data: BookCreateSchema, file_path: str = None) -> Optional[Book]:
        """
        Create new book
        
        Args:
            book_data: Book creation data
            file_path: Path to book file
            
        Returns:
            Created book object or None
        """
        try:
            book = Book(
                title=book_data.title,
                author=book_data.author,
                description=book_data.description,
                category_id=book_data.category_id,
                isbn=book_data.isbn,
                publisher=book_data.publisher,
                pages=book_data.pages,
                language=book_data.language,
                file_type=book_data.file_type,
                file_path=file_path,
                status=BookStatus.PENDING
            )
            self.db.add(book)
            self.db.commit()
            self.db.refresh(book)
            logger.info(f"Created book: {book.id} - {book.title}")
            return book

        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            self.db.rollback()
            return None

    async def update_book(self, book_id: int, update_data: BookUpdateSchema) -> Optional[Book]:
        """
        Update book information
        
        Args:
            book_id: Book ID
            update_data: Update data
            
        Returns:
            Updated book object or None
        """
        try:
            book = await self.get_book(book_id)
            if not book:
                return None

            update_dict = update_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(book, key, value)

            self.db.commit()
            self.db.refresh(book)
            logger.info(f"Updated book: {book_id}")
            return book

        except Exception as e:
            logger.error(f"Error updating book: {str(e)}")
            self.db.rollback()
            return None

    async def delete_book(self, book_id: int) -> bool:
        """
        Delete book
        
        Args:
            book_id: Book ID
            
        Returns:
            True if successful
        """
        try:
            book = await self.get_book(book_id)
            if not book:
                return False

            self.db.delete(book)
            self.db.commit()
            logger.info(f"Deleted book: {book_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting book: {str(e)}")
            self.db.rollback()
            return False

    async def increment_download_count(self, book_id: int) -> bool:
        """
        Increment book download count
        
        Args:
            book_id: Book ID
            
        Returns:
            True if successful
        """
        try:
            book = await self.get_book(book_id)
            if not book:
                return False

            book.download_count += 1
            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error incrementing download count: {str(e)}")
            self.db.rollback()
            return False

    async def add_review(self, book_id: int, user_id: int, title: str, content: str) -> Optional[Review]:
        """
        Add review to book
        
        Args:
            book_id: Book ID
            user_id: User ID
            title: Review title
            content: Review content
            
        Returns:
            Created review or None
        """
        try:
            review = Review(
                book_id=book_id,
                user_id=user_id,
                title=title,
                content=content
            )
            self.db.add(review)
            
            # Update book review count
            book = await self.get_book(book_id)
            if book:
                book.total_reviews += 1
            
            self.db.commit()
            self.db.refresh(review)
            logger.info(f"Added review to book {book_id}")
            return review

        except Exception as e:
            logger.error(f"Error adding review: {str(e)}")
            self.db.rollback()
            return None

    async def add_rating(self, book_id: int, user_id: int, rating: int) -> Optional[Rating]:
        """
        Add rating to book
        
        Args:
            book_id: Book ID
            user_id: User ID
            rating: Rating (1-5)
            
        Returns:
            Created rating or None
        """
        try:
            # Check if user already rated this book
            existing_rating = self.db.query(Rating).filter(
                Rating.book_id == book_id,
                Rating.user_id == user_id
            ).first()

            if existing_rating:
                # Update existing rating
                existing_rating.rating = rating
                rating_obj = existing_rating
            else:
                # Create new rating
                rating_obj = Rating(
                    book_id=book_id,
                    user_id=user_id,
                    rating=rating
                )
                self.db.add(rating_obj)

            # Update book average rating
            book = await self.get_book(book_id)
            if book:
                all_ratings = self.db.query(Rating).filter(Rating.book_id == book_id).all()
                if all_ratings:
                    avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings)
                    book.average_rating = round(avg_rating, 1)

            self.db.commit()
            self.db.refresh(rating_obj)
            logger.info(f"Added rating to book {book_id}")
            return rating_obj

        except Exception as e:
            logger.error(f"Error adding rating: {str(e)}")
            self.db.rollback()
            return None

    async def get_featured_books(self, limit: int = 10) -> List[Book]:
        """
        Get featured books
        
        Args:
            limit: Number of books to return
            
        Returns:
            List of featured books
        """
        try:
            books = self.db.query(Book).filter(
                Book.status == BookStatus.ACTIVE,
                Book.is_featured == True
            ).order_by(Book.download_count.desc()).limit(limit).all()
            return books

        except Exception as e:
            logger.error(f"Error getting featured books: {str(e)}")
            return []

    async def get_trending_books(self, limit: int = 10) -> List[Book]:
        """
        Get trending books
        
        Args:
            limit: Number of books to return
            
        Returns:
            List of trending books
        """
        try:
            books = self.db.query(Book).filter(
                Book.status == BookStatus.ACTIVE
            ).order_by(Book.download_count.desc()).limit(limit).all()
            return books

        except Exception as e:
            logger.error(f"Error getting trending books: {str(e)}")
            return []

    async def get_books_by_category(self, category_id: int, limit: int = 20, offset: int = 0) -> List[Book]:
        """
        Get books by category
        
        Args:
            category_id: Category ID
            limit: Number of books
            offset: Offset for pagination
            
        Returns:
            List of books in category
        """
        try:
            books = self.db.query(Book).filter(
                Book.category_id == category_id,
                Book.status == BookStatus.ACTIVE
            ).order_by(Book.created_at.desc()).limit(limit).offset(offset).all()
            return books

        except Exception as e:
            logger.error(f"Error getting books by category: {str(e)}")
            return []
