import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Session, Base
from database_handler import DatabaseHandler
from database_analysis import DataAnalysis
import create_datebase as db_creator
from models.exam import Exam
from models.student import Student

engine = create_engine(f'sqlite:///student_db.sqlite')
Session = sessionmaker(bind=engine)


def import_to_sql(xlsx_name="new_data1", db_name='student_db.sqlite'):
    # Инициализируем базу данных
    Base.metadata.create_all(engine)

    # Замените "students.xlsx" на имя вашего файла Excel
    excel_file = f'{xlsx_name}.xlsx'
    session = Session()
    # Читаем данные из Excel в DataFrame
    sheet_names = ['students', 'scores', 'exams', 'school_exams']
    for sheet_name in sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df.to_sql(sheet_name, con=engine, if_exists='append', index=False)

    # Фиксируем изменения в базе данных
    session.commit()
    return session


def export_to_excel(sqlite_file='student_train1', start_id=1, end_id=10):
    table_names = ["students", "scores", "exams", "school_exams"]

    with pd.ExcelWriter("student_analysis.xlsx", engine='xlsxwriter') as writer:
        for table_name in table_names:
            if table_name != 'students':
                query = f"SELECT * FROM {table_name} WHERE student_id >= {start_id} AND student_id <= {end_id}"
            else:
                query = f"SELECT * FROM {table_name} WHERE id >= {start_id} AND id <= {end_id}"
            df = pd.read_sql_query(query, con=engine)
            sheet_name = table_name

            df.to_excel(writer, sheet_name=sheet_name, index=False)


def predict_for_excel(name='student_db', model_type='knn', limit=10, xlsx_file='new_data1'):
    session = import_to_sql(xlsx_name=xlsx_file, db_name=name)

    students = session.query(Student).all()

    database_analysis = DataAnalysis(session)
    database_handler = DatabaseHandler(session)
    count = 0
    for student in students:

        if count == limit:
            break
        predict = database_analysis.general_predict(student.id, model_type, False)
        database_handler.add_prediction_student(student.id, predict)

        exams = session.query(Exam).filter_by(student_id=student.id).all()

        for exam in exams:
            predict = database_analysis.subject_predict(student.id, exam.subject_id, f'{model_type}_subject', False)
            database_handler.add_prediction_subject(student.id, exam.subject_id, predict)
        count += 1


def main():
    while True:
        print("1. Импортировать данные в SQLite")
        print("2. Проанализировать данные и экспортировать в Excel")
        print("3. Поработать с базой в консоли")
        print("4. Выйти")
        choice = input("Введите команду (1/2/3/4): ")

        if choice == '1':
            xlsx_name = input("Введите название файла для импорта: ")
            import_to_sql(xlsx_name)
            print("Данные импортированы!")
        elif choice == '2':
            xlsx_file = input("Введите название файлы Excel: ")
            sqlite_file = input("Введите название SQLite файла: ")
            predict_for_excel(sqlite_file, 'knn', 10, xlsx_file)
            export_to_excel(sqlite_file)
            print("Данные проанализированы и экспортированы в Excel!")
        elif choice == '3':
            handler()
        elif choice == '4':
            break
        else:
            print("Ошибка! Попробуйте выбрать снова.")


def print_menu():
    print("1. Просмотреть информацию о студенте")
    print("2. Добавить нового студента")
    print("3. Удалить студента")
    print("4. Просмотреть информацию о предмете")
    print("5. Добавить новый предмет")
    print("6. Добавить баллы за предмет")
    print("7. Просмотреть информацию об экзамене")
    print("8. Добавить баллы за экзамен")
    print("9. Просмотреть все группы")
    print("10. Просмотреть всех студентов в группе")
    print("0. Выйти")


def handler():
    session = Session()
    db_handler = DatabaseHandler(session)

    while True:
        print_menu()
        choice = input("Введите номер действия (0-10): ")

        if choice == "1":
            student_id = int(input("Введите ID студента: "))
            db_handler.print_student_info(student_id)
        elif choice == "2":
            student_name = input("Введите имя студента: ")
            group_id = int(input("Введите ID группы: "))
            # Дополнительные вопросы для добавления студента
            # ...
            db_handler.add_student(student_name, group_id, {}, 0)  # Передайте необходимые параметры
        elif choice == "3":
            student_id = int(input("Введите ID студента для удаления: "))
            db_handler.delete_student(student_id)
        elif choice == "4":
            subject_id = int(input("Введите ID предмета: "))
            # Дополнительные вопросы для просмотра информации о предмете
            # ...
            db_handler.print_subject_info(subject_id)
        elif choice == "5":
            subject_name = input("Введите название предмета: ")
            db_handler.add_subject(subject_name)
        elif choice == "6":
            # Дополнительные вопросы для добавления баллов за предмет
            # ...
            db_handler.add_score_in_subject(0, 0, "Название предмета")
        elif choice == "7":
            exam_id = int(input("Введите ID экзамена: "))
            # Дополнительные вопросы для просмотра информации об экзамене
            # ...
            db_handler.print_exam_info(exam_id)
        elif choice == "8":
            # Дополнительные вопросы для добавления баллов за экзамен
            # ...
            db_handler.add_score_in_exam(0, 0, "Название предмета")
        elif choice == "9":
            db_handler.print_all_data("Группы")
        elif choice == "10":
            group_id = int(input("Введите ID группы: "))
            db_handler.print_all_data("Студенты", group_id)
        elif choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод. Пожалуйста, введите число от 0 до 10.")


if __name__ == '__main__':
    main()

