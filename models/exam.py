from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class Exam(Base):
    __tablename__ = 'exams'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship('Student', back_populates='exams')
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    subject = relationship('Subject', back_populates='exams')
    exam_scores = Column(Integer)
    attending_classes = Column(Integer)
