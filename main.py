import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Session, Base
from database_handler import DatabaseHandler
from database_analysis import DataAnalysis
from models.exam import Exam
from models.score import Score
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
        print("3. Выйти")
        choice = input("Введите команду (1/2/3): ")

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
            break
        else:
            print("Ошибка! Попробуйте выбрать снова.")


if __name__ == '__main__':
    main()






    '''db_is_created = os.path.exists("student_train1.sqlite")
    if db_is_created:
        print(f'База с именем student_train1.sqlite существует')
    else:
        print('Создаю базу...')
        db_creator.create_database()
    session = Session()
    database_analysis = DataAnalysis(session)
    database_handler = DatabaseHandler(session)
    database_analysis.train('svr')
    database_analysis.train_subject(1, 'svr_subject')
    database_analysis.train_subject(2, 'svr_subject')
    database_analysis.train_subject(3, 'svr_subject')
    database_analysis.train_subject(4, 'svr_subject')

    print(database_analysis.general_predict(1))
    print(database_analysis.general_predict(2))
    print(database_analysis.general_predict(3))

    list_exams = {'Русский': 40, 'Математика': 40, 'Информатика': 40, 'Физика': 0}
    database_handler.delete_student(501)
    database_handler.add_student('студент', 1,
                                 list_exams,
                                 1, True)
    database_handler.add_score_in_subject(501, 40, 'Предмет0')
    database_handler.add_score_in_subject(501, 40, 'Предмет1')
    database_handler.add_score_in_subject(501, 40, 'Предмет2')
    database_handler.add_score_in_subject(501, 40, 'Предмет3')
    #predict = database_analysis.general_predict(501, 'svr')
    #database_handler.add_prediction_student(501, predict)
    #database_handler.print_student_info(501)

    #print(database_analysis.general_predict(1))
    database_handler.print_student_info(1)
    database_handler.add_score_in_exam(1, 0, 'Предмет0')
    database_handler.add_score_in_exam(1, 0, 'Предмет1')
    database_handler.add_score_in_exam(1, 0, 'Предмет2')
    database_handler.add_score_in_exam(1, 0, 'Предмет3')
    print()
    print(database_analysis.subject_predict(1, 1, 'knn_subject'))
    print(database_analysis.subject_predict(1, 2, 'knn_subject'))
    print(database_analysis.subject_predict(1, 3, 'knn_subject'))
    print(database_analysis.subject_predict(1, 4, 'knn_subject'))
    print()
    database_handler.print_student_info(2)
    database_handler.add_score_in_exam(2, 0, 'Предмет0')
    database_handler.add_score_in_exam(2, 0, 'Предмет1')
    database_handler.add_score_in_exam(2, 0, 'Предмет2')
    database_handler.add_score_in_exam(2, 0, 'Предмет3')

    print(database_analysis.subject_predict(2, 1, 'knn_subject'))
    print(database_analysis.subject_predict(2, 2, 'knn_subject'))
    print(database_analysis.subject_predict(2, 3, 'knn_subject'))
    print(database_analysis.subject_predict(2, 4, 'knn_subject'))

    database_handler.add_prediction_subject(2, 1, predict=database_analysis.subject_predict(2, 1, 'knn_subject'))
'''
