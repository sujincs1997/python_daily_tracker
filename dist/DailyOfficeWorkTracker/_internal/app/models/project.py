from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(150), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    tasks = relationship("Task", back_populates="project")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.project_name}', active={self.active})>"
