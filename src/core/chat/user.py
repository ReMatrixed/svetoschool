# Подключение модулей библиотеки aiogram
from aiogram import types, F
from aiogram import Router, Bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums.parse_mode import ParseMode
import aiogram.exceptions

# Подключение core-библиотек
from core.db.connector import DatabaseConnector
from core.db.exceptions import UserNotFound, TaskNotFound
from core.manager.locale import LocaleManager
from core.presets.states import UserContext, MemberContext
from core.presets.keyboard import ReplyKeyboard
from core.presets.datatypes import UserData, TaskData
from core.presets.enums import UserRole, DatabaseTable, TaskStatus

# Подключение встроенных библиотек
import re
import logging

# Настройка логгера
logger = logging.getLogger("user.py")

# Инициализация Router'а для обычных пользователей
router_user = Router()

# Паттерн для проверки ответов пользователя на соостветствование требованиям
regex_cyrillic = re.compile(r"[^а-яёА-ЯЁ\s-]|[\s{2,}] ")

# Handler для сообщения с ответом на вопрос об классе обучения (1-й вопрос)
@router_user.message(StateFilter(UserContext.setup_form))
async def user_survey_form(message: types.Message, state: FSMContext, locale: LocaleManager):
    if(message.text.isdigit()): # Проверка на то, является ли ответ пользователя числом
        user_answer = int(message.text) # Преобразование текстового ответа пользователя в число
        if(user_answer >= 1 and user_answer <= 11): # Проверка на валидность значения класса
            await state.update_data(form = user_answer)
            await message.reply(locale.get("greeting.survey.city"))
            await state.set_state(UserContext.setup_city)
        else:
            await message.reply(locale.get("global.error.invalid_data"))
    else:
        await message.reply(locale.get("global.error.invalid_data"))

# Handler для сообщения с ответом на вопрос о городе обучения
@router_user.message(StateFilter(UserContext.setup_city))
async def user_survey_city(message: types.Message, state: FSMContext, locale: LocaleManager):
    if(re.search(regex_cyrillic, message.text) == None): # Проверка на соответствие требованиям
        await state.update_data(city = message.text.upper()) # Запись преобразованного значения в FSM
        await message.reply(
            locale.get("greeting.survey.optional_data"), 
            reply_markup = ReplyKeyboard.selection_simple
        ) 
        await state.set_state(UserContext.setup_optional_data)
    else:
        await message.reply(locale.get("global.error.invalid_data"))

# Callback для ответа на сообщение, касающегося дополнительного опроса
@router_user.callback_query(StateFilter(UserContext.setup_optional_data), F.data.startswith("callback_selection_"))
@router_user.callback_query(StateFilter(UserContext.setup_realname), F.data.startswith("callback_selection_"))
async def setup_user_optional_data( 
    callback: types.CallbackQuery, state: FSMContext,
    locale: LocaleManager, db_connector: DatabaseConnector
):
    await callback.answer()
    user_choice = callback.data.replace("callback_selection_", "")
    if(user_choice == "n"):
        fsm_data = await state.get_data()
        user_data = UserData(
            chat_id = callback.from_user.id, 
            role = UserRole.ROLE_USER.value, 
            rating = 100, 
            form = fsm_data.get("form"), 
            city = fsm_data.get("city"),
            realname = "Аноним",
            is_admin = False,
            is_blocked = False
        )
        await db_connector.update_user(user_data)
        await callback.message.reply(locale.get("greeting.survey.finish"))
        await state.set_state(UserContext.dialog_question)
    elif(user_choice == "y"):
        await callback.message.reply(locale.get("greeting.survey.realname"))
        await state.set_state(UserContext.setup_realname)

# Handler для сообщения с ответом на вопрос об имени и фамилии
@router_user.message(StateFilter(UserContext.setup_realname))
async def setup_user_realname( 
    message: types.Message, state: FSMContext,
    locale: LocaleManager, db_connector: DatabaseConnector
):
    if(re.search(regex_cyrillic, message.text) == None):
        await state.update_data(realname = message.text.title())
        fsm_data = await state.get_data()
        await db_connector.update_user(
            UserData(
                chat_id = message.from_user.id,
                role = UserRole.ROLE_USER.value,
                rating = 100,
                form = fsm_data.get("form"),
                city = fsm_data.get("city"),
                realname = fsm_data.get("realname"),
                is_admin = False,
                is_blocked = False
            )
        )
        await message.reply(locale.get("greeting.survey.finish"))
        await state.set_state(UserContext.dialog_question)
    else:
        await message.reply(locale.get("global.error.invalid_data"))

# Handler для получения текста запроса от пользователя
# Проверки, которые проводятся во время обработки запроса:
# 1. Проверка текста по мат-фильтру (resources/ru/censorship.txt)
@router_user.message(StateFilter(UserContext.dialog_question))
async def get_user_question(
    message: types.Message, state: FSMContext,
    locale: LocaleManager, db_connector: DatabaseConnector
):
    await db_connector.delete(message.from_user.id, DatabaseTable.TABLE_TASKS) # Удалить запись запроса, если таковой существует
    if(locale.check(message.text)):
        await state.update_data(question = message.text)
        await message.reply(locale.get("request.user.subject"), reply_markup = ReplyKeyboard.selection_subject)
        await state.set_state(UserContext.dialog_subject)
    else:
        user_data = await db_connector.get_user(message.from_user.id)
        user_data.rating -= 5
        await db_connector.update_user(user_data)
        await message.reply(locale.get("global.error.bad_language").replace("$$1", str(user_data.rating)))

# Handler для команды об отмене запроса (task)
@router_user.message(Command("cancel_request"), StateFilter(UserContext.dialog_wait))
async def cancel_user_request(
    message: types.Message, state: FSMContext,
    locale: LocaleManager, db_connector: DatabaseConnector
):
    try:
        task_data = await db_connector.get_task(message.from_user.id)
        if(task_data.status == TaskStatus.TASK_PENDING.value):
            await db_connector.delete(message.from_user.id, DatabaseTable.TABLE_TASKS)
            await message.reply(locale.get("request.user.cancel.success"))
            await state.set_state(UserContext.dialog_question)
        elif(task_data.status == TaskStatus.TASK_DELEGATED.value):
            # TODO: Добавить оповещение исполнителю об отмене запроса,
            # а также запросить подтверждение у пользователя (необязательно)
            pass
        elif(task_data.status == TaskStatus.TASK_ACCEPTED.value):
            # TODO: Добавить оповещение в диалоге об отмене запроса,
            # запросить подтверждение у пользователя,
            # начислить штраф за некорректное завершение диалога (необязательно)
            pass    
    except TaskNotFound:
        await message.reply(locale.get("request.user.cancel.not_found"))

# Handler для ответа на пользовательские сообщения, отправленные во время ожидания ответа на запрос
@router_user.message(StateFilter(UserContext.dialog_wait))
async def answer_to_waiting_user(message: types.Message, locale: LocaleManager):
    await message.reply(locale.get("request.user.wait"))

# Handler для ответа от пользователя на вопрос о предмете
@router_user.callback_query(
    StateFilter(UserContext.dialog_subject), 
    F.data.startswith("callback_subject_")
)
async def get_question_subject(
    callback: types.CallbackQuery, state: FSMContext,
    locale: LocaleManager, db_connector: DatabaseConnector
):
    await callback.answer()
    fsm_data = await state.get_data()
    await db_connector.update_task(
        TaskData(
            chat_id = callback.from_user.id,
            subject = callback.data.replace("callback_subject_", "").upper()[0],
            question = fsm_data.get("question"),
            priority = 0,
            status = TaskStatus.TASK_PENDING.value,
            member = 0
        )
    )
    await callback.message.reply(locale.get("request.user.pending"))
    await state.set_state(UserContext.dialog_wait)

# Handler для ответа на команду от пользователя об остановке диалога
@router_user.message(Command("stop_dialog"), StateFilter(UserContext.dialog_proceed))
async def stop_user_dialog( 
    message: types.Message, state: FSMContext, bot: Bot,
    locale: LocaleManager, db_connector: DatabaseConnector, 
    fsm_storage: RedisStorage,
):
    fsm_data = await state.get_data()
    try:
        await bot.send_message(
            fsm_data.get("user_id"), 
            locale.get("dialog.member.was_stopped_by_user")
        )
    except aiogram.exceptions.TelegramBadRequest:
            logger.warning(locale.get("logger.warning.missing_user").replace("$$1", fsm_data.get("user_id")))
    member_state = FSMContext(
        fsm_storage, 
        StorageKey(
            bot_id = bot.id, 
            chat_id = fsm_data.get("user_id"),
            user_id = fsm_data.get("user_id")
        )
    )
    await message.reply(locale.get("dialog.user.stop"))
    await member_state.set_state(MemberContext.dialog_rate)
    await state.set_state(UserContext.dialog_rate)
    await db_connector.delete(DatabaseTable.TABLE_TASKS, message.from_user.id)

# Handler для передачи сообщений от пользователя к эксперту во время диалога
@router_user.message(StateFilter(UserContext.dialog_proceed))
async def proceed_user_dialog(message: types.Message, state: FSMContext, bot: Bot):
    fsm_data = await state.get_data()
    await bot.send_message(fsm_data.get("user_id"), message.md_text, parse_mode = ParseMode.MARKDOWN_V2)

# Handler для ответа на пользовательскую оценку деятельности эксперта
@router_user.message(StateFilter(UserContext.dialog_rate))
async def get_rate_by_user(
    message: types.Message, state: FSMContext,
    locale: LocaleManager
):
    if(message.text.isdigit()):
        user_rating = int(message.text)
        if(user_rating > 0 and user_rating < 11):
            # TODO: Обновление рейтинга эксперта в БД
            await message.reply(locale.get("dialog.user.rate"))
            await state.set_state(UserContext.dialog_question)
        else:
            await message.reply(locale.get("global.error.invalid_data"))
    else:
        await message.reply(locale.get("global.error.invalid_data"))