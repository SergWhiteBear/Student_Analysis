import joblib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from models.student import Student
from database_handler import DatabaseHandler as dh


# DONE
def evaluate_model(model, X, y, model_name):
    """
    Оценивает производительность модели с использованием MAE.
    """
    predictions = model.predict(X)
    mae = mean_absolute_error(y, predictions)
    mse = mean_squared_error(y, predictions)
    print(f"{model_name} - MAE: {mae} - MSE: {mse}")
    r2 = r2_score(y, predictions)

    print(f"R^2: {r2}")


class DataAnalysis:
    def __init__(self, session):
        self.feature_names_before_scaling = None
        self.feature_names = None
        self.session = session
        self.model = None
        self.feature_scaler = MinMaxScaler()
        self.target_scaler = MinMaxScaler()
        self.dh = dh()

    def __del__(self):
        self.session.close()

    def preprocess_data(self, df, is_training: bool = True):
        """
        Предобработка данных для последующего анализа
        """
        # Удаляем столбец 'name', так как он не является числовым признаком
        df = df.drop(['name'], axis=1)

        # Сохраняем имена признаков перед масштабированием
        self.feature_names_before_scaling = df.columns.tolist()

        # Рассчитываем среднее значение для каждого списка оценок
        df['semester_scores'] = df['semester_scores'].apply(lambda scores: np.mean(scores) if len(scores) > 0 else 0)
        df['ege_scores'] = df['ege_scores'].apply(lambda scores: np.mean(scores) if len(scores) > 0 else 0)
        df['exam_scores'] = df['exam_scores'].apply(lambda scores: np.mean(scores) if len(scores) > 0 else 0)
        df['attending_classes'] = df['attending_classes'].apply(
            lambda scores: np.mean(scores) if len(scores) > 0 else 0)

        # Добавляем столбец 'olympiad' со значением 0, если его нет
        if 'olympiad' not in df.columns:
            df['olympiad'] = 0

        # Удаляем строки с отсутствующими значениями
        df.dropna(inplace=True)

        # Нормализуем выбранные признаки с использованием сохраненных имен признаков
        scaled_features = self.feature_scaler.fit_transform(df[['semester_scores', 'ege_scores',
                                                                'olympiad', 'attending_classes']])

        df[['semester_scores', 'ege_scores', 'olympiad', 'attending_classes']] = scaled_features

        # Нормализуем целевую переменную
        df['exam_scores'] = self.target_scaler.fit_transform(df[['exam_scores']])

        # Переименовываем столбцы для удобства
        df.columns = ['semester_scores', 'ege_scores', 'exam_scores', 'olympiad', 'attending_classes']

        if is_training:
            # Сохраняем имена признаков, увиденные во время обучения
            self.feature_names = df.columns.tolist()

        return df

    def train(self, model_type: str):
        """
        Тренировка модели, есть возможность выбрать тип модели
        """
        # Извлекаем данные всех студентов из базы данных
        students = self.session.query(Student).all()
        # Преобразуем данные студентов в формат DataFrame
        students_data = [{'name': student.name,
                          'semester_scores': [score.value for score in student.scores],
                          'ege_scores': [school_exam.score_exam for school_exam in student.school_exams],
                          'exam_scores': [score.exam_scores for score in student.exams],
                          'olympiad': int(student.olympiad) if student.olympiad else 0,
                          'attending_classes': [exam.attending_classes for exam in student.exams]} for student in
                         students]
        df = pd.DataFrame(students_data)

        # Предварительная обработка данных
        df = self.preprocess_data(df)

        # Разделяем данные на признаки (X) и целевую переменную (y)
        X = df[['semester_scores', 'ege_scores', 'olympiad', 'attending_classes']]
        y = df['exam_scores'].values.flatten()
        # Разделяем данные на обучающий и тестовый наборы
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Выбираем тип модели в зависимости от переданного параметра
        if model_type == 'linear_regression':
            self.model = LinearRegression()
        elif model_type == 'svr':
            self.model = SVR()
        elif model_type == 'knn':
            self.model = KNeighborsRegressor(n_neighbors=5)  # Вы можете изменить количество соседей

        # Обучаем модель
        try:
            self.model.fit(X_train, y_train)
        except Exception as e:
            print(f'Возникла ошибка \n{e}')

        # Оценка производительности модели на тестовом наборе данных
        evaluate_model(self.model, X_test, y_test, model_type)

        self.save_model(model_type)
        # График фактических и предсказанных значений
        predictions = self.model.predict(X_test)
        self.plot_predictions(y_test, predictions, model_type)

    def general_predict(self, student_id: int, model_type: str = 'svr', train_model: bool = False):
        """
        Общий вывод по данным, т.е. прогноз среднего балла за экзамены
        """
        if train_model:
            self.train(model_type)
        else:
            self.load_model(model_type)
        # Извлекаем данные по конкретному студенту из базы данных
        student = self.session.query(Student).filter_by(id=student_id).first()
        # Преобразуем данные студента в формат DataFrame
        student_data = {
            'name': student.name,
            'semester_scores': [score.value for score in student.scores],
            'ege_scores': [school_exam.score_exam for school_exam in student.school_exams],
            'exam_scores': [score.exam_scores for score in student.exams],
            'olympiad': int(student.olympiad) if student.olympiad else 0,
            'attending_classes': [exam.attending_classes for exam in student.exams]
        }
        df_student = pd.DataFrame([student_data])

        # Выводим данные студента для отладки
        # print(df_student)

        # Обеспечиваем, чтобы имена признаков соответствовали тем, которые были видны во время обучения
        df_student = self.preprocess_data(df_student, is_training=False)

        # Масштабируем признаки студента
        X_student = df_student[['semester_scores', 'ege_scores',
                                'olympiad', 'attending_classes']]
        # Предсказываем нормализованные значения
        prediction_normalized = self.model.predict(X_student)

        # Инвертируем масштаб, чтобы получить исходную шкалу
        prediction = self.target_scaler.inverse_transform(prediction_normalized.reshape(-1, 1))

        # Выводим масштабированные предсказанные значения
        if prediction[0][0] < 1:
            prediction = prediction[0][0] * 100
        else:
            prediction = prediction[0][0]

        # Теперь прогноз будет сразу записываться к студенту в базу
        self.dh.add_prediction_student(student_id, prediction)

        return prediction

    def train_subject(self, subject_id: int, model_type: str = 'svr_subject'):
        """
        Тренировка модели, есть возможность выбрать тип модели
        """
        # Извлекаем данные всех студентов из базы данных
        students = self.session.query(Student).all()
        # Преобразуем данные студентов в формат DataFrame
        students_data = [{
            'name': student.name,
            'semester_scores': [score.value for score in student.scores if subject_id == score.subject_id],
            'ege_scores': [school_exam.score_exam for school_exam in student.school_exams],
            'exam_scores': [score.exam_scores for score in student.exams if subject_id == score.subject_id],
            'olympiad': int(student.olympiad) if student.olympiad else 0,
            'attending_classes': [exam.attending_classes for exam in student.exams]
        } for student in students]
        df = pd.DataFrame(students_data)

        # Предварительная обработка данных
        df = self.preprocess_data(df)

        # Разделяем данные на признаки (X) и целевую переменную (y)
        X = df[['semester_scores', 'ege_scores', 'olympiad', 'attending_classes']]
        y = df['exam_scores'].values.flatten()
        # Разделяем данные на обучающий и тестовый наборы
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Выбираем тип модели в зависимости от переданного параметра
        if model_type == 'linear_regression_subject':
            self.model = LinearRegression()
        elif model_type == 'svr_subject':
            self.model = SVR()
        elif model_type == 'knn_subject':
            self.model = KNeighborsRegressor(n_neighbors=5)

        # Обучаем модель
        try:
            self.model.fit(X_train, y_train)
        except Exception as e:
            print(f'Возникла ошибка \n{e}')

        self.save_model(model_type)

        # Оценка производительности модели на тестовом наборе данных
        evaluate_model(self.model, X_test, y_test, model_type)

        # График фактических и предсказанных значений
        predictions = self.model.predict(X_test)
        self.plot_predictions(y_test, predictions, model_type)

    def subject_predict(self, student_id: int, subject_id: int, model_type: str = 'svr_subject', train_model: bool = False):
        if train_model:
            self.train_subject(subject_id, model_type)
        else:
            self.load_model(model_type)

        # Извлекаем данные по конкретному студенту из базы данных
        student = self.session.query(Student).filter_by(id=student_id).first()
        # Преобразуем данные студента в формат DataFrame
        student_data = {
            'name': student.name,
            'semester_scores': [score.value for score in student.scores if subject_id == score.subject_id],
            'ege_scores': [school_exam.score_exam for school_exam in student.school_exams],
            'exam_scores': [score.exam_scores for score in student.exams if subject_id == score.subject_id],
            'olympiad': int(student.olympiad) if student.olympiad else 0,
            'attending_classes': [exam.attending_classes for exam in student.exams]
        }
        df_student = pd.DataFrame([student_data])

        # Выводим данные студента для отладки
        # print(df_student)

        # Обеспечиваем, чтобы имена признаков соответствовали тем, которые были видны во время обучения
        df_student = self.preprocess_data(df_student, is_training=False)

        # Масштабируем признаки студента
        X_student = df_student[['semester_scores', 'ege_scores', 'olympiad', 'attending_classes']]
        # Предсказываем нормализованные значения
        prediction_normalized = self.model.predict(X_student)

        # Инвертируем масштаб, чтобы получить исходную шкалу
        prediction = self.target_scaler.inverse_transform(prediction_normalized.reshape(-1, 1))

        # Выводим масштабированные предсказанные значения
        if prediction[0][0] < 1:
            prediction = prediction[0][0] * 100
        else:
            prediction = prediction[0][0]

        # Теперь прогноз для предмета у студента записывается сразу в базу
        self.dh.add_prediction_subject(student_id, subject_id, prediction)

        return prediction

    @staticmethod
    def plot_predictions(actual, predicted, model_name):
        """
        Создает график фактических и предсказанных значений для визуального сравнения.
        """
        plt.scatter(actual, predicted, label=model_name)
        plt.xlabel('Фактические значения')
        plt.ylabel('Предсказанные значения')
        plt.title(f'Фактические vs Предсказанные - {model_name}')
        plt.legend()
        plt.show()

    def save_model(self, model_type):
        """
        Сохранение модели
        """
        if self.model is not None:
            model_filename = f"{model_type}_model.pkl"
            joblib.dump(self.model, model_filename)
            print(f"Модель сохранена в файл: {model_filename}")
        else:
            print("Ошибка: Модель не обучена.")

    def load_model(self, model_type):
        """
        Загрузка сохраненной модели
        """
        model_filename = f"{model_type}_model.pkl"
        try:
            self.model = joblib.load(model_filename)
            print(f"Модель загружена из файла: {model_filename}")
        except FileNotFoundError:
            print("Ошибка: Файл с моделью не найден.")
            print("Тренируем модель...")
            self.train(model_type)
        except Exception as e:
            print(f"Ошибка при загрузке модели: {e}")
