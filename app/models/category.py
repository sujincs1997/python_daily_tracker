from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False, unique=True)

    # Relationships
    tasks = relationship("Task", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.category_name}')>"
