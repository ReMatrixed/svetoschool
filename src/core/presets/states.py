# Подключение модулей для работы с FSM-состояниями из aiogram
from aiogram.fsm.state import State, StatesGroup

# Состояния FSM, предназначенные для общения с пользователем (role: user)
class UserContext(StatesGroup):
    setup_welcome = State() # Запрос разрешения на получения данных о пользователе
    setup_form = State() # Запрос номера класса обучения
    setup_city = State() # Запрос названия города проживания
    setup_optional_data = State() # Запрос на сбор дополнительных данных
    setup_realname = State() # Запрос имени и фамилии (необязательно)
    dialog_question = State() # Запрос вопроса для эксперта
    dialog_subject = State() # Запрос категории вопроса (школьный предмет)
    dialog_wait = State() # Ответ пользователю во время ожидания рассмотрения запроса
    dialog_proceed = State() # Запрос сообщений для передачи эксперту
    dialog_rate = State() # Запрос оценки деятельности эксперта (необязательно)

# Состояния FSM, предназначенные для общения с пользователем (role: member)
class MemberContext(StatesGroup):
    dialog_wait = State() # Ожидание запросов от пользователей
    dialog_request_permission = State() # Ожидание принятия запроса экспертом
    dialog_proceed = State() # Запрос сообщений для передачи пользователю
    dialog_rate = State() # Запрос оценки пользователя (необязательно)

# Состояния FSM, предназначенные для общения с администратором (role: admin)
class AdminContext(StatesGroup):
    command_selection = State() # Выбор команды управления
    command_modify_search = State()
    command_modify_select = State()
    command_modify_entity = State()
    command_modify_member_subjects = State()
    command_modify_member_status = State()
    command_modify_user_transition = State()
    command_modify_user_block = State()
    command_modify_user_delete = State()
    command_modify_user_rename = State()