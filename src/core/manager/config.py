# Подключение библиотек для работы с переменными среды
from dotenv import load_dotenv
import os

# Подключение библиотеки для работы с аннотациями типов
from typing import Union

# Подключение библиотеки для работы с журналом (логгирования)
import logging

# Подключение библиотеки для работы с системой
import sys

class ConfigManager:
    logger: logging.Logger # Обработчик журнала (логгер)

    # Инициализация обработчика с использованием системных переменных среды (docker environment, например)
    def setup(self) -> None:
        self.logger = logging.getLogger("config.py")
        self.logger.info("Подготовка обработчика конфигураций (режим: классический)...")
        self.logger.info("Обработчик конфигураций инициализирован.")

    # Инициализация обработчика с использованием файла .env
    def setup_env(self, filepath: str) -> None:
        self.logger = logging.getLogger("config.py")
        self.logger.info("Подготовка обработчика конфигураций (режим: dotenv)...")
        self.logger.info(f"Чтение файла переменных среды: {filepath}...")
        if(load_dotenv(filepath) == False):
            self.logger.critical(f"Ошибка чтения файла {filepath}: Файл не найден")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы
        self.logger.info("Обработчик конфигураций инициализирован.")

    # Получить значение из конфигурационных данных по ключу
    def get(self, key: str) -> Union[str, int]:
        try:
            return os.environ[key] # Получение значения из переменных среды
        except KeyError:
            self.logger.critical(f"Ошибка получения конфигурационных данных: Ключ {key} не найден")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы