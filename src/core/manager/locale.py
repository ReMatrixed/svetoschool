# Подключение библиотеки для работы с JSON-файлами
import json
from json.decoder import JSONDecodeError

# Подключение библиотеки для работы с журналом (логгирования)
import logging

# Подключение библиотеки для работы с системой
import sys

class LocaleManager:
    locale: dict[str, str] # Словарь для хранения языковых данных
    blacklist: list[str]   # Список запрещённых частей слов
    logger: logging.Logger # Обработчик журнала (логгер)

    # Инициализация обработчика, чтение языковых данных
    def setup(self, resources_filepath: str) -> None:
        # Сборка пути до языковых файлов
        filepath_locale = f"{resources_filepath}/locale.json"
        filepath_blacklist = f"{resources_filepath}/blacklist.txt"
        
        self.logger = logging.getLogger("locale.py")
        self.logger.info("Подготовка обработчика языковых данных...")
        self.logger.info(f"Чтение файла локализации: {filepath_locale}...")
        try:
            with open(filepath_locale, "r") as locale_file:
                self.locale = json.load(locale_file)
        # Так как файл локализации (сообщения, тексты журнала) крайне важен,
        # программа завершает работу при возникновении ошибки чтения данного файла
        except FileNotFoundError:
            self.logger.critical("Ошибка чтения файла с языковыми данными: Файл не найден")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы
        except JSONDecodeError as e:
            self.logger.critical(f"Ошибка JSON-парсинга файла с языковыми данными: ({e})")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы

        self.logger.info(f"Чтение файла цензуры (мат-фильтр) ({filepath_blacklist})...")
        try:
            with open(filepath_blacklist, "r") as blacklist_file:
                self.blacklist = blacklist_file.read().splitlines()
        # Так как фильтр цензуры достаточно важен, программа завершает
        # свою работу при возникновении ошибки чтения данного файла
        except FileNotFoundError:
            self.logger.critical("Ошибка чтения цензор-файла: Файл не найден")
            self.logger.info("Завершение работы...")
            sys.exit() # Безопасное завершение работы программы
        self.logger.info("Обработчик языковых данных инициализирован.")

    # Получить значение из словаря по ключу
    def get(self, key: str) -> str:
        return self.locale.get(key, "UNKNOWN")
    
    # Проверить строку на наличие запрещенных слов
    def check(self, text: str) -> bool:
        for word in self.blacklist:
            if(word in text.lower()):
                return False
        return True