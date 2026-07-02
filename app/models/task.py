from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False)
    task_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    assigned_by_id = Column(Integer, ForeignKey("assigned_by.id"), nullable=False)
    
    priority = Column(String(50), nullable=False)  # Low, Medium, High, Critical
    status = Column(String(50), nullable=False)    # Not Started, In Progress, Paused, Completed, Cancelled
    completion = Column(Integer, default=0, nullable=False)  # 0 to 100
    
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, default=0, nullable=False)  # Duration in seconds
    
    remarks = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    assigned_by = relationship("AssignedBy", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, number='{self.task_number}', title='{self.title}', status='{self.status}')>"
