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
from core.manager.locale import LocaleManager
from core.presets.states import UserContext, MemberContext
from core.presets.enums import DatabaseTable, MemberStatus, TaskStatus

# Подключение встроенных библиотек
import logging

# Инициализация Router'а для пользователей-экспертов
router_member = Router()

# Настройка логгера
logger = logging.getLogger("member.py")

# Handler для ответа на команду от эксперта об остановке диалога
@router_member.message(Command("stop_dialog"), StateFilter(MemberContext.dialog_proceed))
async def stop_member_dialog(
    message: types.Message, state: FSMContext, bot: Bot,
    locale: LocaleManager, db_connector: DatabaseConnector, 
    fsm_storage: RedisStorage
):
    fsm_data = await state.get_data()
    try:
        await bot.send_message(
            fsm_data.get("user_id"), 
            locale.get("dialog.user.was_stopped_by_member")
        )
    except aiogram.exceptions.TelegramBadRequest:
            logger.warning(locale.get("logger.warning.missing_user").replace("$$1", str(fsm_data.get("user_id"))))
    user_state = FSMContext(
        fsm_storage, 
        StorageKey(
            bot_id = bot.id, 
            chat_id = fsm_data.get("user_id"),
            user_id = fsm_data.get("user_id")
        )
    )
    await message.reply(locale.get("dialog.member.stop"))
    await user_state.set_state(UserContext.dialog_rate)
    await state.set_state(MemberContext.dialog_rate)
    await db_connector.delete(fsm_data.get("user_id"), DatabaseTable.TABLE_TASKS)

# Handler для ответа на вопрос об принятии пользовательского запроса экспертом
# TODO: Обновить блок кода с использованием try-except
@router_member.callback_query(
    StateFilter(MemberContext.dialog_request_permission), 
    F.data.startswith("callback_selection_")
)
async def get_member_dialog_permission(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot, 
    fsm_storage: RedisStorage, db_connector: DatabaseConnector, locale: LocaleManager
):
    await callback.answer()
    fsm_data = await state.get_data()
    user_state = FSMContext(
        fsm_storage, 
        StorageKey(
            bot_id = bot.id,
            chat_id = fsm_data.get("user_id"),
            user_id = fsm_data.get("user_id")
        )
    )
    user_data = await db_connector.get_user(callback.from_user.id)
    member_choice = callback.data.replace("callback_selection_", "")
    if(member_choice == "accept"):
        await callback.message.answer(locale.get("dialog.member.permission.accept"))
        await db_connector.set_task_status(fsm_data.get("user_id"), TaskStatus.TASK_ACCEPTED)
        await user_state.update_data(user_id = callback.from_user.id)
        await user_state.set_state(UserContext.dialog_proceed)
        try:
            await bot.send_message(
                fsm_data.get("user_id"), 
                locale.get("request.user.was_accepted")
                    .replace("$$1", user_data.realname)
                    .replace("$$2", str(user_data.rating))
                    .replace("$$3", str(user_data.form))
            )
        except aiogram.exceptions.TelegramBadRequest:
            logger.warning(locale.get("logger.warning.missing_user").replace("$$1", str(fsm_data.get("user_id"))))
        await state.set_state(MemberContext.dialog_proceed)
    elif(member_choice == "transfer"):
        await db_connector.set_member_status(callback.from_user.id, MemberStatus.MEMBER_PAUSED)
        await db_connector.set_task_status(fsm_data.get("user_id"), TaskStatus.TASK_PENDING)
        await callback.message.answer(locale.get("dialo.member.permission.transfer"))
    elif(member_choice == "decline"):
        await db_connector.delete(fsm_data.get("user_id"), DatabaseTable.TABLE_TASKS)
        await db_connector.set_member_status(callback.from_user.id, MemberStatus.MEMBER_AVAILABLE)
        try:
            await bot.send_message(fsm_data.get("user_id"), locale.get("request.user.was_rejected"))
        except aiogram.exceptions.TelegramBadRequest:
            logger.warning(locale.get("logger.warning.missing_user").replace("$$1", str(fsm_data.get("user_id"))))
        await user_state.set_state(UserContext.dialog_question)
        await callback.message.answer(locale.get("dialog.member.permission.decline"))
        await state.set_state(MemberContext.dialog_wait)

# Handler для передачи сообщений от эксперта к пользователю
@router_member.message(StateFilter(MemberContext.dialog_proceed))
async def proceed_member_dialog(message: types.Message, state: FSMContext, bot: Bot, locale: LocaleManager):
    fsm_data = await state.get_data()
    try:
        await bot.copy_message(fsm_data.get("user_id"), message.from_user.id, message.message_id, parse_mode = ParseMode.MARKDOWN_V2)
    except aiogram.exceptions.TelegramBadRequest:
        logger.warning(locale.get("logger.warning.missing_user").replace("$$1", str(fsm_data.get("user_id"))))

# Handler для ответа на оценку пользователя экспертом
@router_member.message(StateFilter(MemberContext.dialog_rate))
async def get_rate_by_member(
    message: types.Message, state: FSMContext,
    locale: LocaleManager, db_connector: DatabaseConnector
):
    if(message.text.isdigit()):
        user_rating = int(message.text)
        if(user_rating > 0 and user_rating < 11):
            # TODO: Обновление рейтинга пользователя в БД
            await message.reply(locale.get("dialog.member.rate"))
            await db_connector.set_member_status(message.from_user.id, MemberStatus.MEMBER_AVAILABLE)
            await state.set_state(MemberContext.dialog_wait)
        else:
            await message.reply(locale.get("global.error.invalid_data"))
    else:
        await message.reply(locale.get("global.error.invalid_data"))