# Подключение модулей библиотеки aiogram
from aiogram import types, F
from aiogram import Router, Bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext

# Подключение core-библиотек
from core.db.connector import DatabaseConnector
from core.db.exceptions import UserNotFound
from core.manager.locale import LocaleManager
from core.presets.states import UserContext, MemberContext
from core.presets.enums import UserRole, MemberStatus

# Подключение встроенных библиотек
import logging

# Инициализация Router'а для пользователей, не имеющих роли 
router_common = Router()

# Настройка логгера
logger = logging.getLogger("common.py")

# Handler для команды /start (перезапуск бота)
@router_common.message(Command("start"))
async def start_bot(
    message: types.Message, state: FSMContext, 
    locale: LocaleManager, db_connector: DatabaseConnector
):
    try:
        user_data = await db_connector.get_user(message.from_user.id)
        if(user_data.role == UserRole.ROLE_USER.value):
            await message.reply(locale.get("greeting.user").replace("$$1", user_data.realname))
            await state.set_state(UserContext.dialog_question)
        elif(user_data.role == UserRole.ROLE_MEMBER.value):
            await message.reply(locale.get("greeting.member").replace("$$1", user_data.realname))
            await state.set_state(MemberContext.dialog_wait)
            await db_connector.set_member_status(user_data.chat_id, MemberStatus.MEMBER_AVAILABLE)
        if(user_data.is_admin):
            await message.answer(locale.get("greeting.admin").replace("$$1", user_data.realname))
    except UserNotFound:
        await message.reply(locale.get("greeting.newbie"))
        await message.answer(locale.get("greeting.survey.form"))
        await state.set_state(UserContext.setup_form)

# Handler для команды /get_chat_id (получение chat_id текущего пользователя)
@router_common.message(Command("get_chat_id"))
async def get_chat_id(message: types.Message, locale: LocaleManager):
    await message.reply(locale.get("special.chat_id").replace("$$1", str(message.from_user.id)))