import os

import numpy as np

from models.database import DATABASE_NAME, Session
import create_datebase as db_creator
from database_handler import DatabaseHandler  # работает
from database_analysis import DataAnalysis

if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if db_is_created:
        print(f'База с именем {DATABASE_NAME} существует')
    else:
        print('Создаю базу...')
        db_creator.create_database()
