# Подключение библиотеки для работы с JSON-файлами
import json
from json.decoder import JSONDecodeError

# Подключение библиотеки логгирования
import logging

# Подключение библиотеки для работы с системой
import sys

class LocaleManager:
    locale: dict[str, str] # Словарь для хранения языковых данных
    blacklist: list[str]   # Список запрещённых частей слов
    logger: logging.Logger # Обработчик журнала (логгер)

    # Инициализация обработчика, чтение языковых данных
    def setup(self, locale_filepath: str, blacklist_filepath) -> None:
        self.logger = logging.getLogger("manager/locale.py")
        self.logger.info("Подготовка обработчика языковых данных...")
        self.logger.info(f"Чтение файла локализации: {locale_filepath}...")
        try:
            with open(locale_filepath, "r") as locale_file:
                self.locale = json.load(locale_file)
        # Так как файл локализации (сообщения, тексты журнала) крайне важен,
        # программа завершает работу при возникновении ошибки чтения данного файла
        except FileNotFoundError:
            self.logger.critical("")
            sys.exit() # Безопасное завершение работы программы
        except JSONDecodeError as e:
            self.logger.critical("")
            sys.exit() # Безопасное завершение работы программы

        self.logger.info(f"Чтение файла цензуры (мат-фильтр) ({blacklist_filepath})...")
        try:
            with open(blacklist_filepath, "r") as blacklist_file:
                self.blacklist = blacklist_file.read().splitlines()
        # Так как фильтр цензуры достаточно важен, программа завершает
        # свою работу при возникновении ошибки чтения данного файла
        except FileNotFoundError:
            self.logger.error("")
            sys.exit()
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