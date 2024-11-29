# Подключение библиотеки для работы с data-классами
from dataclasses import dataclass

# Подключение необходимых перечислений
from .enums import UserRole, SchoolSubject, TaskStatus

# Сведения об зарегистрированном пользователе
@dataclass
class UserData:
    chat_id: int = None
    role: UserRole = UserRole.ROLE_USER
    rating: int = 100
    realname: str = "Неизвестно"
    form: int = -1
    city: str = "Неизвестен"
    is_admin: bool = False
    is_blocked: bool = False

# Сведения об эксперте (member) чат-центра
@dataclass
class MemberData:
    chat_id: int = None
    subjects: list[str] = None
    answers: int = 0
    images: int = 0
    videos: int = 0
    status: str = 0

# Сведения о пользовательском запросе
@dataclass
class TaskData:
    chat_id: int = None
    subject: str = SchoolSubject.SUBJECT_UNKNOWN.value
    question: str = "Неизвестен"
    priority: int = -1
    status: TaskStatus = TaskStatus.TASK_PENDING
    member: int = None