from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.database import Base


class Score(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    subject = relationship('Subject', back_populates='scores')
    # exam_id = Column(Integer, ForeignKey('exams.id'))
    # exam = relationship('Exam', back_populates='scores')
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship('Student', back_populates='scores')
