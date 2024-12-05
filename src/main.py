# Подключение внутренних модулей
from core.manager.config import ConfigManager
from core.manager.locale import LocaleManager
from core.db.connector import DatabaseConnector

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
    config_manager = config_manager,
    locale_manager = locale_manager,
    db_connector = db_connector
)
# Добавление role-specific Router'ов в корневой Router
bot_dispatcher.include_router(router_admin)
bot_dispatcher.include_router(router_member)
bot_dispatcher.include_router(router_user)
bot_dispatcher.include_router(router_common)
# Настройка параметров бота (API-ключ, режим форматирования)
bot = Bot(
    config_manager.get("TELEGRAM_BOT_API_KEY"),
    default = DefaultBotProperties(parse_mode = ParseMode.HTML)
)

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

    # Запуск задач-демонов
    await asyncio.gather(bot_dispatcher.start_polling(bot))

    # Подготовка таблиц базы данных
    await db_connector.prepare()

    # Отключение от базы данных
    await db_connector.close()

# Начальная точка запуска программы
if __name__ == "__main__":
    asyncio.run(prepare_services())