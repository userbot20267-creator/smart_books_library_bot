from sqlalchemy.orm import Session
from app.models.book import BookCategory

class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, name: str, name_ar: str = None) -> BookCategory:
        cat = BookCategory(name=name, name_ar=name_ar)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    async def update(self, cat_id: int, **kwargs) -> BookCategory | None:
        cat = self.db.query(BookCategory).get(cat_id)
        if not cat:
            return None
        for k, v in kwargs.items():
            if hasattr(cat, k):
                setattr(cat, k, v)
        self.db.commit()
        return cat

    async def delete(self, cat_id: int) -> bool:
        cat = self.db.query(BookCategory).get(cat_id)
        if not cat:
            return False
        self.db.delete(cat)
        self.db.commit()
        return True

    async def list_all(self):
        return self.db.query(BookCategory).all()
