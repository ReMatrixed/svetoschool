# Подключение библиотеки для работы с JSON-файлами
import json
from json.decoder import JSONDecodeError

# Подключение библиотеки для работы с аннотациями типов
from typing import Union

# Подключение библиотеки для работы с журналом (логгирования)
import logging

# Подключение библиотеки для работы с системой
import sys

class ConfigManager:
    config: dict[str, Union[str, int]] # Словарь доступных параметров
    logger: logging.Logger # Обработчик журнала (логгер)

    # Инициализация обработчика, чтение файла конфигурации
    def setup(self, filepath: str) -> None:
        self.logger = logging.getLogger("manager/config.py")
        self.logger.info("Подготовка обработчика конфигураций...")
        self.logger.info(f"Чтение файла конфигурации: {filepath}...")
        try:
            with open(filepath, "r") as config_file:
                self.config = json.load(config_file)
        # Так как файл конфигурации критически важен,
        # программа завершает работу при возникновении ошибки чтения данного файла
        except FileNotFoundError:
            self.logger.critical("Ошибка чтения файла конфигурации: Файл не найден")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы
        except JSONDecodeError as e:
            self.logger.critical(f"Ошибка JSON-парсинга файла конфигурации: ({e})")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы
        self.logger.info("Обработчик конфигураций инициализирован.")

    # Получить значение из конфигурационных данных по ключу
    def get(self, key: str) -> Union[str, int]:
        try:
            return self.config[key]
        except KeyError:
            self.logger.critical(f"Ошибка получения конфигурационных данных: Ключ {key} не найден")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы