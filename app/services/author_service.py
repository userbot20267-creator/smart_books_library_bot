from sqlalchemy.orm import Session
from app.models.author import Author

class AuthorService:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, name: str, bio: str = None) -> Author:
        author = Author(name=name, bio=bio)
        self.db.add(author)
        self.db.commit()
        self.db.refresh(author)
        return author

    async def update(self, author_id: int, **kwargs) -> Author | None:
        author = self.db.query(Author).get(author_id)
        if not author:
            return None
        for k, v in kwargs.items():
            if hasattr(author, k):
                setattr(author, k, v)
        self.db.commit()
        return author

    async def delete(self, author_id: int) -> bool:
        author = self.db.query(Author).get(author_id)
        if not author:
            return False
        self.db.delete(author)
        self.db.commit()
        return True

    async def list_all(self):
        return self.db.query(Author).all()
