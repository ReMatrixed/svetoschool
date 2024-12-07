# Подключение встроенной библиотеки enum для работы с перечислениями
from enum import Enum

# Доступные для использования состояния запроса (task)
class TaskStatus(Enum):
    TASK_PENDING = "P"   # Запрос в очереди, ожидает эксперта-исполнителя
    TASK_DELEGATED = "D" # Запрос ожидает своего принятия экспертом-исполнителем
    TASK_ACCEPTED = "A"  # Запрос выполняется, идет диалог пользователь-эксперт
    # Проверить, существует ли значение в данном перечислении
    @classmethod
    def is_exists(cls, key: str):
        return key in cls.__members__
    
# Доступные для использования статусы запроса на верификацию
class VerificationStatus(Enum):
    REQUEST_PENDING = "P"  # Запрос ожидает рассмотрения администратором
    REQUEST_REVIEW = "R"   # Запрос на рассмотрении у администратора
    REQUEST_ACCEPTED = "A" # Запрос принят администратором (пользователь верифицирован)
    REQUEST_REJECTED = "R" # Запрос отклонён администратором
    # Проверить, существует ли значение в данном перечислении
    @classmethod
    def is_exists(cls, key: str):
        return key in cls.__members__

# Доступные для использования причины отклонения запросов на верификацию
class VerificationRejectReason(Enum):
    INCORRECT_FORM = "F"     # Некорректные сведения о классе обучения
    INCORRECT_CITY = "C"     # Некорректные сведения о городе обучения
    INCORRECT_REALNAME = "R" # Некорректные сведения об имени/фамилии
    INCORRECT_SCHOOL = "S"   # Некорректные сведения о школе обучения
    # Проверить, существует ли значение в данном перечислении
    @classmethod
    def is_exists(cls, key: str):
        return key in cls.__members__


# Доступные для использования роли (типы) пользователей
class UserRole(Enum):
    ROLE_MEMBER = "M" # Пользователь-эксперт
    ROLE_USER = "U" # Обычный пользователь
    # Проверить, существует ли значение в данном перечислении
    @classmethod
    def is_exists(cls, key: str):
        return key in cls.__members__

# Доступные для использования статусы эксперта
class MemberStatus(Enum):
    MEMBER_AVAILABLE = "A"   # Эксперт свободен, ожидает запроса
    MEMBER_WORKING = "W"     # Эксперт занят, отвечает на запрос
    MEMBER_PAUSED = "P"      # Эксперт временно недоступен (например, находится в отпуске)
    MEMBER_FIRED = "F"       # Эксперт был уволен из чат-центра
    MEMBER_UNAVAILABLE = "U" # Эксперт недоступен (вероятнее всего использует панель управления)
    # Проверить, существует ли значение в данном перечислении
    @classmethod
    def is_exists(cls, key: str):
        return key in cls.__members__

# Доступные для использования таблицы базы данных
class DatabaseTable(Enum):
    TABLE_USERS = "users"     # Таблица, хранящая список зарегистрированных пользователей
    TABLE_MEMBERS = "members" # Таблица, хранящая список пользователей-экспертов
    TABLE_TASKS = "tasks"     # Таблица, хранящая список запросов от пользователей
    # Проверить, существует ли значение в данном перечислении
    @classmethod
    def is_exists(cls, key: str):
        return key in cls.__members__

# Доступные для выбора школьные предметы
class SchoolSubject(Enum):
    SUBJECT_MATHS = "M"
    SUBJECT_ENGLISH = "E"
    SUBJECT_PHYSICS = "P"
    SUBJECT_RUSSIAN = "R"
    SUBJECT_BIOLOGY = "B"
    SUBJECT_SOCIAL = "S"
    SUBJECT_HISTORY = "H"
    SUBJECT_CHEMISTRY = "C"
    SUBJECT_INFORMATICS = "I"
    SUBJECT_GEOGRAPHY = "G"
    SUBJECT_UNKNOWN = "X"
    SUBJECT_FUNCTIONALITY = "F" # Тех. поддержка
    # Проверить, существует ли значение в данном перечислении
    @classmethod
    def is_exists(cls, key: str):
        return key in cls.__members__
    
# Расшифровка различных сокращений
class Namer():
    subjects = {
        "M": "Математика",
        "I": "Информатика",
        "P": "Физика",
        "G": "География",
        "C": "Химия",
        "B": "Биология",
        "H": "История",
        "S": "Обществознание",
        "R": "Русский язык",
        "E": "Английский язык",
        "F": "Тех. поддержка"
    }

    member_status = {
        "A": "Доступен",
        "W": "Работает",
        "P": "Отдыхает",
        "F": "Уволен",
        "U": "Недоступен"
    }

    user_role_emoji = {
        "U": "👤 Пользователь",
        "M": "🎓 Эксперт"
    }