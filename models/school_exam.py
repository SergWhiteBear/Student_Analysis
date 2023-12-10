from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class School_exam(Base):
    __tablename__ = 'school_exams'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship('Student', back_populates='school_exams')
    exam_name = Column(String)
    score_exam = Column(Integer)
