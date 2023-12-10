from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models.database import Base


class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    scores = relationship('Score', back_populates='subject', cascade='all, delete-orphan')
    exams = relationship('Exam', back_populates='subject', cascade='all, delete-orphan')
