# Основной класс исключений БД
class DatabaseException(Exception):
    """Base Exception class for DatabaseConnector.

    Args:
        msg (str): Message of the exception
    """

# Класс исключений, возникающих при попытке обращения к несуществующей записи в БД
class EntryNotFound(DatabaseException):
    """Base Exception class for missing entries in table

    Args:
        DatabaseException (_type_): _description_
    """

# Исключение, возвращаемое когда пользователь не найден в таблице
class UserNotFound(EntryNotFound):
    """Exception raised when chat_id in users table is not found.

    Args:
        msg (str): Message of the exception
    """

# Исключение, возвращаемое когда эксперт не найден в таблице
class MemberNotFound(EntryNotFound):
    """Exception raised when chat_id in members table is not found.

    Args:
        msg (str): Message of the exception
    """

# Исключение, возвращаемое когда запрос не найден в таблице
class TaskNotFound(EntryNotFound):
    """Exception raised when chat_id in tasks table is not found.

    Args:
        msg (str): Message of the exception
    """

class SelectionError(DatabaseException):
    """Exception raised when there is no selectable values in the table.

    Args:
        msg (str): Message of the exception
    """

class TaskSelectionError(SelectionError):
    """Exception raised when there is no selectable tasks.

    Args:
        msg (str): Message of the exception
    """

class MemberSelectionError(SelectionError):
    """Exception raised when there is no selectable members.

    Args:
        msg (str): Message of the exception
    """