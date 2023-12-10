import random
from faker import Faker

from models.database import create_db, Session
from models.subject import Subject
from models.student import Student

from models.exam import Exam
from models.score import Score
from models.school_exam import School_exam
from models.group import Group


def create_database(load_fake_data: bool = True):
    create_db()
    if load_fake_data:
        generate_fake_data(Session())


def generate_fake_data(session, num_groups=4, num_students=500, num_subjects=4):
    fake = Faker('ru_RU')

    # Создание групп
    groups = [Group(name=f'group{i}') for i in range(num_groups)]
    session.add_all(groups)
    session.commit()

    # Создание студентов
    list_val = [True, False]
    students = [Student(name=fake.name(), olympiad=random.choice(list_val),
                        group_id=fake.random_element(elements=[group.id for group in groups]), general_predict=0) for _
                in range(num_students)]
    session.add_all(students)
    session.commit()

    # Создание предметов
    subjects = [Subject(name=f'Предмет{i}') for i in range(num_subjects)]
    session.add_all(subjects)
    session.commit()

    # Перемешивание студентов и предметы, чтобы равномерно распределить экзамены
    random.shuffle(students)
    random.shuffle(subjects)

    # Создание экзаменов
    exams = []
    for student in students:
        for subject in subjects:
            exam = Exam(student_id=student.id, subject_id=subject.id, exam_scores=fake.random_int(40, 100),
                        attending_classes=fake.random_int(0, 10), subject_predict=0)
            #exam = Exam(student_id=student.id, subject_id=subject.id, exam_scores=0,
                       # attending_classes=fake.random_int(0, 10), subject_predict=0)
            exams.append(exam)
            session.add(exam)
    session.commit()

    for exam in exams:
        score = Score(value=fake.random_int(min=0, max=100), subject_id=exam.subject_id,
                      student_id=exam.student_id)
        #score = Score(value=0, subject_id=exam.subject_id,
                    #  student_id=exam.student_id)
        session.add(score)
    session.commit()

    list_school_exams = ['Математика', 'Русский', 'Информатика', 'Физика']
    for student in students:
        for i in range(4):
            school_exam = School_exam(student_id=student.id, exam_name=list_school_exams[i],
                                      score_exam=fake.random_int(50, 100))
            session.add(school_exam)
    session.commit()

    session.close()
