from models.database import Session
from models.student import Student
from models.subject import Subject
from models.school_exam import School_exam
from models.exam import Exam
from models.score import Score


# DONE
class DatabaseHandler:
    def __init__(self):
        self.session = Session()

    def __del__(self):
        self.session.close()

    def print_student_info(self, student_id: int):
        student = self.find_student_by_id(student_id)

        if student:
            # Выводим информацию о студенте
            print(f"Имя студента: {student.name}")
            print(f"Баллы за семестр: {[score.value for score in student.scores]}")
            print(f"Баллы за ЕГЭ: {[school_exam.score_exam for school_exam in student.school_exams]}")
            print(f"Баллы за экзамены: {[score.exam_scores for score in student.exams]}")
            print(f"Участие в олимпиадах: {int(student.olympiad) if student.olympiad else 0}")
            print(f"Посещение занятий: {[exam.attending_classes for exam in student.exams]}")
        else:
            print(f"Студент с идентификатором {student_id} не найден.")

    def find_student_by_name(self, student_name: str):
        student = Student
        try:
            student = self.session.query(Student).filter_by(name=student_name).first()
        except Exception as e:
            print(f'Такого студента нет \n{e}')
        return student

    def find_student_by_id(self, student_id: int):
        student = Student()
        try:
            student = self.session.query(Student).filter_by(id=student_id).first()
        except Exception as e:
            print(f'Такого студента нет \n{e}')
        return student

    def add_student(self, student_name: str, group_id: int, list_school_exams: list, take_part_olympiad: int,
                    add_subjects: bool = True):
        new_student = Student(name=student_name, olympiad=take_part_olympiad, group_id=group_id)
        self.session.add(new_student)
        self.session.commit()
        for name_exam, score_exam in list_school_exams[0].items():
            school_exam = School_exam(student_id=new_student.id, exam_name=name_exam,
                                      score_exam=score_exam)
            self.session.add(school_exam)
        if add_subjects:
            subjects = self.session.query(Subject).all()

            exams = []
            for subject in subjects:
                exam = Exam(student_id=new_student.id, subject_id=subject.id, exam_scores=0, attending_classes=0)
                exams.append(exam)
                self.session.add(exam)
                self.session.commit()

            for exam in exams:
                score = Score(value=0, subject_id=exam.subject_id,
                              student_id=exam.student_id)
                self.session.add(score)
            self.session.commit()

        self.session.commit()

    def delete_student(self, student_id: int):
        student = self.session.query(Student).get(student_id)
        if student:
            self.session.delete(student)
            self.session.commit()
            return True
        return False

    def find_subject_by_name(self, subject_name: str):
        subject = Subject()
        try:
            subject = self.session.query(Subject).filter_by(name=subject_name).first()
        except Exception as e:
            print(f'Такого предмета нет \n{e}')
        return subject

    def find_subject_by_id(self, subject_id: int):
        subject = Subject()
        try:
            subject = self.session.query(Subject).filter_by(subject_id=subject_id).first()
        except Exception as e:
            print(f'Такого предмета нет \n{e}')
        return subject

    def add_subject(self, subject_name: str, add_all_student: bool = True):
        new_subject = Subject(name=subject_name)
        self.session.add(new_subject)
        self.session.commit()
        if add_all_student:
            self.add_new_subject_for_all_students(new_subject)
        return new_subject

    def add_score_in_subject(self, student_id: int, value: int, subject_name: str, ):
        subject = self.find_subject_by_name(subject_name)
        existing_score = self.session.query(Score).filter_by(student_id=student_id, subject_id=subject.id).first()

        if existing_score:
            # Если сущность существует, обновляем ее значение
            existing_score.value = value
        else:
            # Иначе создаем новую сущность
            score = Score(value=value, subject_id=subject.id, student_id=student_id)
            self.session.add(score)

        self.session.commit()

    def add_score_in_exam(self, student_id: int, value: int, subject_name: str, attending_classes=10):
        subject = self.find_subject_by_name(subject_name)

        existing_exam = self.session.query(Exam).filter_by(student_id=student_id, subject_id=subject.id).first()

        if existing_exam:
            # Если сущность существует, обновляем ее значение
            existing_exam.exam_scores = value
        else:
            # Иначе создаем новую сущность
            subject = Exam(exam_scores=value,
                           subject_id=subject.id,
                           student_id=student_id,
                           attending_classes=attending_classes)
            self.session.add(subject)

        self.session.commit()

    def add_new_subject_for_all_students(self, new_subject: str):
        self.session.add(new_subject)
        self.session.commit()

        students = self.session.query(Student).all()
        for student in students:
            exam = Exam(student_id=student.id,
                        subject_id=new_subject.id,
                        exam_scores=0,
                        attending_classes=0)
            self.session.add(exam)
            self.session.commit()

            score = Score(value=0,
                          subject_id=new_subject.id,
                          student_id=student.id)
            self.session.add(score)
            self.session.commit()

    def delete_subject(self, subject_id: int, subject_name: str):
        subject = Subject()
        if subject_id is not None:
            subject = self.session.query(Subject).get(subject_id)
        elif subject_id is None and subject_name is not None:
            subject = self.session.query(Subject).get(subject_name)
        else:
            print('Предупреждение! Такого предмета нет')
        if subject:
            self.session.delete(subject)
            self.session.commit()
            return True
        return False
