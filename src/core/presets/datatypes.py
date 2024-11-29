# Подключение библиотеки для работы с датами
from datetime import date

# Подключение библиотеки для работы с data-классами
from dataclasses import dataclass

# Сведения об зарегистрированном пользователе
@dataclass
class UserData:
    chat_id: int
    role: str
    rating: int
    realname: str
    form: int
    city: str
    is_admin: bool
    is_blocked: bool

# Сведения об эксперте (member) чат-центра
@dataclass
class MemberData:
    chat_id: int
    subjects: list[str]
    answers: int
    images: int
    videos: int
    status: str

# Сведения о пользовательском запросе
@dataclass
class TaskData:
    chat_id: int
    subject: str
    question: str
    priority: int
    status: str
    member: int

# Сведения о заблокированном пользователе
@dataclass
class BlockData:
    chat_id: int
    until: date
    reason: str

# Сведения о запросе на верификацию
@dataclass
class VerificationData:
    chat_id: int
    updated: date
    status: str
    reason: str