"""Search Service Module - Handles different search types"""

import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.book import Book, BookStatus
from .ai_service import AIService

logger = logging.getLogger(__name__)


class SearchService:
    """Service for book search operations"""

    def __init__(self, db: Session):
        """Initialize search service"""
        self.db = db
        self.ai_service = AIService()

    async def text_search(self, query: str, limit: int = 20, offset: int = 0) -> List[Book]:
        """
        Perform text search on books
        
        Args:
            query: Search query
            limit: Number of results to return
            offset: Offset for pagination
            
        Returns:
            List of books matching query
        """
        try:
            logger.info(f"Text search for: {query}")
            
            books = self.db.query(Book).filter(
                Book.status == BookStatus.ACTIVE,
                (Book.title.ilike(f"%{query}%")) |
                (Book.author.ilike(f"%{query}%")) |
                (Book.description.ilike(f"%{query}%")) |
                (Book.ai_tags.ilike(f"%{query}%"))
            ).limit(limit).offset(offset).all()
            
            return books

        except Exception as e:
            logger.error(f"Error in text search: {str(e)}")
            return []

    async def semantic_search(self, query: str, limit: int = 20, offset: int = 0) -> List[Book]:
        """
        Perform semantic search using embeddings
        
        Args:
            query: Search query
            limit: Number of results to return
            offset: Offset for pagination
            
        Returns:
            List of books matching query semantically
        """
        try:
            logger.info(f"Semantic search for: {query}")
            
            # Generate embeddings for query
            query_embedding = await self.ai_service.generate_embeddings(query)
            if not query_embedding:
                logger.warning("Failed to generate query embeddings")
                return await self.text_search(query, limit, offset)

            # Get all active books
            books = self.db.query(Book).filter(
                Book.status == BookStatus.ACTIVE,
                Book.embedding_vector.isnot(None)
            ).all()

            # Calculate similarity scores
            results = []
            for book in books:
                if book.embedding_vector:
                    try:
                        book_embedding = eval(book.embedding_vector)
                        score = self.ai_service.similarity_score(query_embedding, book_embedding)
                        results.append((book, score))
                    except Exception as e:
                        logger.error(f"Error parsing embedding for book {book.id}: {str(e)}")
                        continue

            # Sort by score and return
            results.sort(key=lambda x: x[1], reverse=True)
            return [book for book, score in results[offset:offset+limit]]

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []

    async def ocr_search(self, image_text: str, limit: int = 20, offset: int = 0) -> List[Book]:
        """
        Perform search based on OCR extracted text
        
        Args:
            image_text: Text extracted from image
            limit: Number of results to return
            offset: Offset for pagination
            
        Returns:
            List of books matching OCR text
        """
        try:
            logger.info(f"OCR search for: {image_text[:100]}")
            
            # Use semantic search for OCR results
            return await self.semantic_search(image_text, limit, offset)

        except Exception as e:
            logger.error(f"Error in OCR search: {str(e)}")
            return []

    async def advanced_search(
        self,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        author: Optional[str] = None,
        language: Optional[str] = None,
        sort_by: str = "relevance",
        limit: int = 20,
        offset: int = 0
    ) -> List[Book]:
        """
        Perform advanced search with multiple filters
        
        Args:
            query: Search query
            category_id: Category filter
            author: Author filter
            language: Language filter
            sort_by: Sort field
            limit: Number of results
            offset: Offset for pagination
            
        Returns:
            List of books matching filters
        """
        try:
            logger.info(f"Advanced search with query={query}, category={category_id}")
            
            filters = [Book.status == BookStatus.ACTIVE]
            
            if query:
                filters.append(
                    (Book.title.ilike(f"%{query}%")) |
                    (Book.author.ilike(f"%{query}%")) |
                    (Book.description.ilike(f"%{query}%"))
                )
            
            if category_id:
                filters.append(Book.category_id == category_id)
            
            if author:
                filters.append(Book.author.ilike(f"%{author}%"))
            
            if language:
                filters.append(Book.language == language)

            query_obj = self.db.query(Book).filter(*filters)

            # Apply sorting
            if sort_by == "rating":
                query_obj = query_obj.order_by(Book.average_rating.desc())
            elif sort_by == "downloads":
                query_obj = query_obj.order_by(Book.download_count.desc())
            elif sort_by == "newest":
                query_obj = query_obj.order_by(Book.created_at.desc())
            else:  # relevance
                query_obj = query_obj.order_by(Book.view_count.desc())

            books = query_obj.limit(limit).offset(offset).all()
            return books

        except Exception as e:
            logger.error(f"Error in advanced search: {str(e)}")
            return []
