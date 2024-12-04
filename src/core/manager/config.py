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

    # Инициализация обработчика, чтение файла конфигурации
    def setup(self, filepath: str) -> None:
        self.logger = logging.getLogger("manager/config.py")
        self.logger.info("Подготовка обработчика конфигураций...")
        self.logger.info(f"Чтение файла переменных среды: {filepath}...")
        if(load_dotenv(filepath) == False):
            self.logger.critical(f"Ошибка чтения файла {filepath}: Файл не найден")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы
        self.logger.info("Обработчик конфигураций инициализирован.")

    # Получить значение из конфигурационных данных по ключу
    def get(self, key: str) -> Union[str, int]:
        try:
            value = os.environ.get(key) # Получение значения из переменных среды
            if(value == None): # Если значение не найдено, вызывается исключение
                raise KeyError
            else: # Если значение найдено, то оно будет возвращено
                return value
        except KeyError:
            self.logger.critical(f"Ошибка получения конфигурационных данных: Ключ {key} не найден")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы