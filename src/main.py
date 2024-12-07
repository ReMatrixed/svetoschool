# Подключение внутренних модулей
from core.manager.config import ConfigManager
from core.manager.locale import LocaleManager
from core.db.connector import DatabaseConnector
from core.db.exceptions import UserNotFound, MemberNotFound, TaskNotFound
from core.db.exceptions import MemberSelectionError, TaskSelectionError
from core.presets.enums import TaskStatus, MemberStatus, SchoolSubject, Namer, DatabaseTable
from core.presets.keyboard import ReplyKeyboard
from core.presets.states import MemberContext

# Подключение Router'ов aiogram для различных ролей пользователей
from core.chat.admin import router_admin
from core.chat.member import router_member
from core.chat.user import router_user
from core.chat.common import router_common

# Подключение модулей библиотеки aiogram для взаимодействия с Telegram Bot API
from aiogram import Dispatcher, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext
import aiogram.exceptions

# Подключение внутренней библиотеки asyncio для работы с корутинами (corutines)
import asyncio

# Подключение библиотеки логгирования
import logging

# Настройка обработчика журнала (логгера)
logging.basicConfig(
    filename = "logs/solarstorm.log", 
    encoding = "utf-8",
    level = logging.INFO,
    format = "%(asctime)s %(levelname)s:%(name)-10s | %(message)s",
    datefmt = "%d-%m-%Y %H:%M:%S"
)
logger = logging.getLogger("main.py")
logger.info("==========================")
logger.info("Запуск бота SvetoSchool...")

# Создание экземпляров классов обработчиков
config_manager = ConfigManager()
locale_manager = LocaleManager()
db_connector = DatabaseConnector()

# Инициализация обработчика языковых данных и обработчика конфигураций
config_manager.setup()
locale_manager.setup(f"resources/{config_manager.get("LANGUAGE")}")

# Инициализация хранилища FSM, подключение к Redis
fsm_storage = RedisStorage(
    Redis(
        host = config_manager.get("REDIS_HOST"),
        port = config_manager.get("REDIS_PORT"),
        password = config_manager.get("REDIS_PASSWORD")
    )
)
# Инициализация корневого Router'а (Dispatcher ), передача contextual-аргументов
bot_dispatcher = Dispatcher(
    storage = fsm_storage,
    locale = locale_manager,
    db_connector = db_connector
)
# Добавление role-specific Router'ов в корневой Router
bot_dispatcher.include_router(router_common)
bot_dispatcher.include_router(router_admin)
bot_dispatcher.include_router(router_member)
bot_dispatcher.include_router(router_user)
# Настройка параметров бота (API-ключ, режим форматирования)
bot = Bot(
    config_manager.get("TELEGRAM_BOT_API_KEY"),
    default = DefaultBotProperties(parse_mode = ParseMode.HTML)
)

# TODO: Перенести TaskDistributor из main.py
# TaskDistributor - асинхронная функция, которая выполняется в фоне.
# Она требуется, чтобы распределять задачи с состоянием P(ending)
async def start_task_distributor():
    # Доступные для выбора школьные предметы
    available_subjects = list(SchoolSubject)
    while(True): # Основной цикл обработки P-задач
        for subject in available_subjects: # Перебор предметов по-одному
            while(True):
                try:
                    selected_task_id = await db_connector.select_task(subject, TaskStatus.TASK_PENDING)
                    selected_task = await db_connector.get_task(selected_task_id)
                    selected_member_id = await db_connector.select_member(subject, MemberStatus.MEMBER_AVAILABLE)
                    selected_user = await db_connector.get_user(selected_task_id)

                    await db_connector.set_member_status(selected_member_id, MemberStatus.MEMBER_WORKING)
                    selected_task.member = selected_member_id
                    selected_task.status = TaskStatus.TASK_DELEGATED.value
                    await db_connector.update_task(selected_task)

                    await bot.send_message(
                        selected_member_id,
                        locale_manager.get("dialog.member.permission")
                            .replace("$$1", selected_user.realname)
                            .replace("$$2", str(selected_user.rating))
                            .replace("$$3", str(selected_user.form))
                            .replace("$$4", selected_user.city)
                            .replace("$$5", selected_task.question)
                            .replace("$$6", Namer.subjects.get(selected_task.subject)),
                        reply_markup = ReplyKeyboard.selection_request_acception
                    )
                    selected_member_state = FSMContext(
                        fsm_storage, 
                        StorageKey(
                            bot_id = bot.id, 
                            chat_id = selected_member_id, 
                            user_id = selected_member_id
                        )
                    )
                    await selected_member_state.update_data(user_id = selected_task_id)
                    await selected_member_state.set_state(MemberContext.dialog_request_permission)
                except (MemberSelectionError, TaskSelectionError):
                    break
                except UserNotFound:
                    await db_connector.delete(selected_task_id, DatabaseTable.TABLE_TASKS)
                except MemberNotFound:
                    pass

        await asyncio.sleep(1) # Задержка между итерациями для предотвращения отказа в обслуживании

# Функция для подготовки и запуска бота
async def prepare_services():
    # Подключение к базе данных
    await db_connector.connect(
        host = config_manager.get("POSTGRES_HOST"),
        port = config_manager.get("POSTGRES_PORT"),
        username = config_manager.get("POSTGRES_USER"),
        password = config_manager.get("POSTGRES_PASSWORD"),
        dbname = config_manager.get("POSTGRES_DB")
    )
    # Подготовка таблиц базы данных
    await db_connector.prepare()

    # Запуск задач-демонов
    await asyncio.gather(
        bot_dispatcher.start_polling(bot),
        start_task_distributor()
    )

    # Отключение от базы данных
    await db_connector.close()

# Начальная точка запуска программы
if __name__ == "__main__":
    asyncio.run(prepare_services())