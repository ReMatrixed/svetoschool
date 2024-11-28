# Подключение внешней библиотеки psycopg для взаимодействия с PostgreSQL
import psycopg

# Подключение внутренних компонентов модуля
from core.db.validation import IpModel
from core.db.exceptions import UserNotFound, MemberNotFound, TaskNotFound

# Подключение библиотеки логгирования
import logging

class DatabaseConnector:
    connection: psycopg.Connection # Подключение к БД
    logger: logging.Logger # Обработчик журнала

    # Подключение к базе данных
    async def connect(
        self, host: str, port: int, username: str, password: str, dbname: str
    ):
        self.connection = await psycopg.AsyncConnection.connect(
            f"host={IpModel(ip = host)} port={port} user={username} password={password} dbname={dbname}"
        )

    # ИНИЦИАЛИЗАЦИЯ ТАБЛИЦ БАЗЫ ДАННЫХ
    # Структура таблицы пользователей (users):
    # 1-й столбец (id) - идентификационный номер записи БД;
    # 2-й столбец (chat_id) - ChatID пользователя в Telegram;
    # 3-й столбец (role) - тип пользователя: U(ser) - обычный пользователь, M(ember) - эксперт чат-центра;
    # 4-й столбец (rating) - рейтинг пользователя (целое число в диапазоне от 0 до 1000);
    # 5-й столбец (form) - номер класса, в котором обучается пользователь (целое число от 1 до 11);
    # 6-й столбец (city) - название города, в котором обучается/проживает пользователь;
    # 7-й столбец (realname) - фамилия и имя пользователя, передаются опционально.

    # Структура таблицы участников чат-центра (members):
    # 1-й столбец (id) - идентификационный номер записи БД;
    # 2-й столбец (chat_id) - ChatID пользователя в Telegram;
    # 3-й столбец (subject) - предмет, на вопросы по которому отвечает участник: MATHS ("M"), INFORMATICS ("I") и так далее;
    # 4-й столбец (answers) - кол-во успешных ответов эксперта;
    # 5-й столбец (images) - кол-во изображений, отправленных экспертом;
    # 6-й столбец (videos) - кол-во видеоматериалов, отправленных экспертом;
    # 7-й столбец (status) - статус эксперта: 
    #   A(vailable) - свободен, готов к принятию запроса, 
    #   W(orking) - работает над запросом, 
    #   P(aused) - временно недоступен (на больничном, в отпуске), 
    #   F(ired) - покинул чат-центр,
    #   U(navailable) - недоступен, наиболее вероятная причина: использует панель управления.

    # Структура таблицы запросов (tasks):
    # 1-й столбец (id) - идентификационный номер записи БД
    # 2-й столбец (chat_id) - ChatID пользователя в Telegram;
    # 3-й столбец (subject) - первая буква названия предмета, по которому задается вопрос: MATHS ("M"), INFORMATICS ("I") и так далее;
    # 4-й столбец (question) - текст запроса (вопрос от пользователя);
    # 5-й столбец (priority) - приоритет запроса, вычисляется при его создании;
    # 6-й столбец (status) - статус запроса: 
    #   A(ccepted) - запрос выполняется,
    #   D(elegeated) - запросу назначен эксперт-исполнитель, который ещё не одобрил выполнение,
    #   P(ending) - запрос находится в очереди;
    # 7-й столбец (member) - ChatID эксперта, принявшего запрос (если запрос ещё не принят, то равняется NULL)
    async def prepare_database(self) -> None:
        async with self.connection.cursor() as cur: 
            self.logger.info("Подготовка базы данных...")
            self.logger.info("Подготовка таблицы users...")
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    role CHAR NOT NULL,
                    rating SMALLINT NOT NULL,
                    form SMALLINT NOT NULL,
                    city TEXT NOT NULL,
                    realname TEXT NOT NULL,
                    is_admin BOOL NOT NULL
                );
                """
            )

            self.logger.info("Подготовка таблицы members...")
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    subjects CHAR[] NOT NULL,
                    answers INTEGER NOT NULL,
                    images INTEGER NOT NULL,
                    videos INTEGER NOT NULL,
                    status CHAR NOT NULL
                );
                """
            )

            self.logger.info("Подготовка таблицы tasks...")
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    subject CHAR NOT NULL,
                    question TEXT NOT NULL,
                    priority SMALLINT NOT NULL,
                    status CHAR NOT NULL,
                    member BIGINT
                )
                """
            )
            self.logger.info("Применение подготовительных изменений в базе данных...")
            await self.connection.commit() # Применение изменений
            self.logger.info("База данных готова.")
    
    # Добавить (обновить) запись в таблице users
    async def update_user_data(self, user_data) -> None:
        pass