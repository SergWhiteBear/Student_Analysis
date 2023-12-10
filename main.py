import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from models.database import DATABASE_NAME, Session, Base
import create_datebase as db_creator
from database_handler import DatabaseHandler  # работает
from database_analysis import DataAnalysis


def export_to_excel():
    sqlite_file = "student_db.sqlite"

    engine = create_engine(f"sqlite:///{sqlite_file}")

    table_names = ["students", "groups", "subjects", "scores", "exams", "school_exams"]

    with pd.ExcelWriter("merged_data.xlsx", engine='xlsxwriter') as writer:
        for table_name in table_names:
            df = pd.read_sql_table(table_name, con=engine)

            sheet_name = table_name

            df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if db_is_created:
        print(f'База с именем {DATABASE_NAME} существует')
    else:
        print('Создаю базу...')
        db_creator.create_database()

    database_analysis = DataAnalysis(Session())

    # database_analysis.train('svr')
    # database_analysis.train_subject(1)

    database_analysis.general_predict(1)
    database_analysis.subject_predict(1, 1)

    '''# Написать сравнение для всех моделей, выбрать лучшую
    database_analysis.train()

    database_analysis.train_subject()'''

    list_exam = {'Русский': 82, 'Математика': 84, 'Информатика': 93}
    database_handler = DatabaseHandler()
    #database_handler.delete_student(501)
    # Добавить студента для демонстрации работы
    '''database_handler.add_student('Pasha', 1, list_exam, 1, True)
    database_handler.add_score_in_subject(501, 88, 'Предмет0')
    database_handler.add_score_in_subject(501, 90, 'Предмет1')
    database_handler.add_score_in_subject(501, 75, 'Предмет2')
    database_handler.add_score_in_subject(501, 56, 'Предмет3')
    print(f"Общий прогноз: {database_analysis.general_predict(501, 'svr', False)}")
    print(f"Прогноз для 1-го предмета: {database_analysis.subject_predict(501, 1)}")
    print(f"Прогноз для 2-го предмета: {database_analysis.subject_predict(501, 2)}")
    print(f"Прогноз для 3-го предмета: {database_analysis.subject_predict(501, 3)}")
    print(f"Прогноз для 4-го предмета: {database_analysis.subject_predict(501, 4)}")'''
