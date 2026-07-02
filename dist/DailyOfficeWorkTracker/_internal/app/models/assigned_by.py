from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class AssignedBy(Base):
    __tablename__ = "assigned_by"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_name = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=True)

    # Relationships
    tasks = relationship("Task", back_populates="assigned_by")

    def __repr__(self) -> str:
        return f"<AssignedBy(id={self.id}, name='{self.person_name}', designation='{self.designation}')>"
