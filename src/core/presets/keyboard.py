# Подключение типов данных из aiogram
from aiogram import types

# Класс, содержащий преднастроенные inline-клавиатуры для сообщений
class ReplyKeyboard:
    # Простой выбор ("Да" или "Нет")
    selection_simple = types.InlineKeyboardMarkup(
        inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "✅ Да", callback_data = "callback_selection_y"),
                types.InlineKeyboardButton(text = "❌ Нет", callback_data = "callback_selection_n")
            ]
        ]
    )

    selection_request_acception = types.InlineKeyboardMarkup(
        inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "✅ Принять", callback_data = "callback_selection_accept"),
                types.InlineKeyboardButton(text = "❌ Отклонить", callback_data = "callback_selection_decline")
            ],
            [types.InlineKeyboardButton(text = "🔑 Передать", callback_data = "callback_selection_transfer")]
        ]
    )

    # Выбор школьного предмета
    selection_subject = types.InlineKeyboardMarkup(
        inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "📐 Математика", callback_data = "callback_subject_maths"),
                types.InlineKeyboardButton(text = "✒️ Русский язык", callback_data = "callback_subject_russian")
            ],
            [
                types.InlineKeyboardButton(text = "🖥️ Информатика", callback_data = "callback_subject_informatics"),
                types.InlineKeyboardButton(text = "💡 Физика", callback_data = "callback_subject_physics")
            ],
            [
                types.InlineKeyboardButton(text = "🌍 География", callback_data = "callback_subject_geography"),
                types.InlineKeyboardButton(text = "💼 Обществознание", callback_data = "callback_subject_social")
            ],
            [
                types.InlineKeyboardButton(text = "🧪 Химия", callback_data = "callback_subject_chemistry"),
                types.InlineKeyboardButton(text = "🌱 Биология", callback_data = "callback_subject_biology")
            ],
            [
                types.InlineKeyboardButton(text = "🎩 Английский язык", callback_data = "callback_subject_english")
            ],
            [
                types.InlineKeyboardButton(text = "🛠 Тех. поддержка", callback_data = "callback_subject_functionality")
            ]
        ]
    )

    # Выбор нового статуса эксперта
    selection_member_status = types.InlineKeyboardMarkup(
        inline_keyboard = [
            [
                types.InlineKeyboardButton(text = "✅ Доступен", callback_data = "callback_member_status_a"),
                types.InlineKeyboardButton(text = "⏳ Отдыхает", callback_data = "callback_member_status_p"),
                types.InlineKeyboardButton(text = "🚩 Уволен", callback_data = "callback_member_status_f")
            ]
        ]
    )

    # Выбор команды в панели управления
    selection_admin_command = types.InlineKeyboardMarkup(
        inline_keyboard = [
            [types.InlineKeyboardButton(text = "👤 Редактировать пользователя", callback_data = "callback_admin_command_edit")],
            [types.InlineKeyboardButton(text = "📜 Получить файл журнала", callback_data = "callback_admin_command_logfile")]
        ]
    )

    # Выбор параметра для редактирования (эксперт)
    selection_edit_member = types.InlineKeyboardMarkup(
        inline_keyboard = [
            [types.InlineKeyboardButton(text = "📚 Редактировать предметы", callback_data = "callback_subject")],
            [types.InlineKeyboardButton(text = "💡 Изменить статус", callback_data = "callback_edit_member_status")],
            [types.InlineKeyboardButton(text = "📜 Узнать статистику эксперта",callback_data = "callback_edit_member_statistics")],
            [types.InlineKeyboardButton(text = "🧩 Назначить администратором", callback_data = "callback_edit_user_admin")],
            [types.InlineKeyboardButton(text = "🔐 Заблокировать пользователя", callback_data = "callback_edit_member_block")],
            [types.InlineKeyboardButton(text = "🚫 Удалить пользователя", callback_data = "callback_edit_member_delete")]
        ]
    )

    # Выбор параметра для редактирования (обычный пользователь)
    selection_edit_user = types.InlineKeyboardMarkup(
        inline_keyboard = [
            [types.InlineKeyboardButton(text = "🎓 Назначить экспертом", callback_data = "callback_edit_user_transition")],
            [types.InlineKeyboardButton(text = "🧩 Назначить администратором", callback_data = "callback_edit_user_admin")],
            [types.InlineKeyboardButton(text = "🔐 Заблокировать пользователя", callback_data = "callback_edit_user_block")],
            [types.InlineKeyboardButton(text = "🚫 Удалить пользователя", callback_data = "callback_edit_user_delete")]
        ]
    )