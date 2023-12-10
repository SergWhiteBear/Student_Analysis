from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.database import Base


class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'))
    olympiad = Column(Boolean)
    group = relationship('Group', back_populates='students')
    exams = relationship('Exam', back_populates='student', cascade='all, delete-orphan')
    scores = relationship('Score', back_populates='student', cascade='all, delete-orphan')
    school_exams = relationship('School_exam', back_populates='student', cascade='all, delete-orphan')