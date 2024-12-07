# Подключение внешней библиотеки psycopg для взаимодействия с PostgreSQL
import psycopg
from psycopg import sql

# Подключение внутренних компонентов модуля
from core.db.exceptions import UserNotFound, MemberNotFound, TaskNotFound

# Подключение модуля типов данных
from core.presets.datatypes import UserData, MemberData, TaskData, BlockData, VerificationData
from core.presets.enums import DatabaseTable, TaskStatus, MemberStatus, UserRole

# Подключение библиотеки логгирования
import logging

class DatabaseConnector:
    connection: psycopg.Connection # Подключение к БД
    logger: logging.Logger # Обработчик журнала

    # Подключение к базе данных (с проверкой IP-адреса на валидность)
    async def connect(
        self, host: str, port: int, username: str, password: str, dbname: str
    ):
        self.logger = logging.getLogger("connector.py")
        self.logger.info("Подключение к базе данных...")
        self.connection = await psycopg.AsyncConnection.connect(
            f"host={host} port={port} user={username} password={password} dbname={dbname}"
        )
        self.logger.info("Соединение с базой данных установлено.")

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

    # Структура таблицы заблокированных пользователей (blocks):
    # 1-й столбец (id) - идентификационный номер записи БД
    # 2-й столбец (chat_id) - ChatID пользователя в Telegram;
    # 3-й столбец (until) - дата, до которой пользователь считается заблокированным. 
    #   Примечание: Если блокировка вечная, то значение равняется infinity;
    # 4-й столбец (reason) - Причина блокировки, среди которых:
    #   L(anguage) - чрезмерное использование нецензурной лексики,
    #   S(pam) - чрезмерное количество отправляемых пользователем сообщений,
    #   T(alking) - некорректная лексика, оскорбления,
    #   R(equests) - чрезмерная отправка бессмысленных запросов;

    # Структура таблицы пользователей, личность и принадлежность к школе
    # которых была подтверждена (verifications). Такие пользователи могут использовать
    # все школьные сервисы платформы в полной мере:
    # 1-й столбец (id) - идентификационный номер записи БД
    # 2-й столбец (chat_id) - ChatID пользователя в Telegram;
    # 3-й столбец (changed) - дата изменения статуса запроса/верификации;
    # 4-й столбец (status) - статус рассмотрения запроса, среди которых:
    #   P(ending) - запрос находится в очереди на рассмотрение,
    #   R(eview) - запрос на рассмотрении у администратора,
    #   A(llowed) - запрос одобрен, пользователь верифицирован,
    #   R(ejected) - запрос отклонён администратором по определённой причине
    # 5-й столбец (reason) - причина отказа (при наличии), среди которых:
    #   F(orm) - некорректные сведения о классе обучения,
    #   C(ity) - некорректные сведения о городе обучения,
    #   R(ealname) - некорректные данные о имени/фамилии,
    #   S(chool) - некорректные данные о школе обучения.
 
    async def prepare(self) -> None:
        async with self.connection.cursor() as cur: 
            self.logger.info("Подготовка таблиц базы данных...")
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
                    is_admin BOOL NOT NULL,
                    is_blocked BOOL NOT NULL
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

            self.logger.info("Подготовка таблицы blocks...")
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS blocks (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    until TIMESTAMP NOT NULL,
                    reason CHAR NOT NULL
                )
                """
            )

            self.logger.info("Подготовка таблицы verifications...")
            await cur.execute(
                """
                CREATE TABLE IF NOT EXISTS verifications (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL UNIQUE,
                    changed TIMESTAMP NOT NULL,
                    status CHAR NOT NULL,
                    reason CHAR NOT NULL
                )
                """
            )

            self.logger.info("Применение подготовительных изменений в базе данных...")
            await self.connection.commit() # Применение изменений
            self.logger.info("База данных готова.")
    
    # Получить запись пользователь в таблице users по chat_id
    async def get_user(self, chat_id: int) -> UserData:
        async with self.connection.cursor() as cur:
            await cur.execute("SELECT * FROM users WHERE chat_id = %s", [chat_id])
            available_data = await cur.fetchone()
            if(available_data != None):
                return UserData(
                    chat_id = available_data[1],
                    role = available_data[2],
                    rating = available_data[3],
                    realname = available_data[4],
                    form = available_data[5],
                    city = available_data[6],
                    is_admin = available_data[7]
                )
            else:
                raise UserNotFound(f"Unknown chat_id: {chat_id}")
            
    # Получить запись эксперта в таблице members по chat_id
    async def get_member(self, chat_id: int) -> MemberData:
        async with self.connection.cursor() as cur:
            await cur.execute("SELECT * FROM members WHERE chat_id = %s", [chat_id])
            available_data = await cur.fetchone()
            if(available_data != None):
                return MemberData(
                    chat_id = available_data[1],
                    subjects = available_data[2],
                    answers = available_data[3],
                    images = available_data[4],
                    videos = available_data[5],
                    status = available_data[6]
                )
            else:
                raise MemberNotFound(f"Unknown chat_id: {chat_id}")
            
    # Получить запись запроса в таблице tasks по chat_id
    async def get_task(self, chat_id: int) -> TaskData:
        async with self.connection.cursor() as cur:
            await cur.execute("SELECT * FROM tasks WHERE chat_id = %s", [chat_id])
            available_data = await cur.fetchone()
            if(available_data != None):
                return TaskData(
                    chat_id = available_data[1],
                    subject = available_data[2],
                    question = available_data[3],
                    priority = available_data[4],
                    status = available_data[5],
                    member = available_data[6]
                )
            else:
                raise TaskNotFound(f"Unknown chat_id: {chat_id}")

    # Добавить (обновить) запись в таблице users
    async def update_user(self, user_data: UserData) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO users (
                    chat_id, role, rating, form, city, realname, is_admin, is_blocked
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET
                    role = EXCLUDED.role
                    rating = EXLUDED.rating
                    form = EXCLUDED.form
                    city = EXCLUDED.city
                    realname = EXCLUDED.realname
                    is_admin = EXCLUDED.is_admin
                    is_blocked = EXLUDED.is_blocked
                """,
                [
                    user_data.chat_id,
                    user_data.role,
                    user_data.rating,
                    user_data.form,
                    user_data.city,
                    user_data.realname,
                    user_data.is_admin,
                    user_data.is_blocked
                ]
            )

    # Добавить (обновить) запись в таблице members
    async def update_member(self, member_data: MemberData) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO members (chat_id, subjects, answers, images, videos, status) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                ON CONFLICT (chat_id) DO UPDATE SET 
                    subjects = EXCLUDED.subjects,
                    answers = EXCLUDED.answers,
                    images = EXCLUDED.images,
                    videos = EXCLUDED.videos,
                    status = EXCLUDED.status
                """,
                [
                    member_data.chat_id,
                    member_data.subjects,
                    member_data.answers,
                    member_data.images,
                    member_data.videos,
                    member_data.status
                ]
            )
            await self.connection.commit()

    # Добавить (обновить) запись в таблице tasks (запросы)  
    async def update_task(self, task_data: TaskData) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO tasks (chat_id, subject, question, priority, status, member)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET
                    subject = EXCLUDED.subject,
                    question = EXCLUDED.question,
                    priority = EXCLUDED.priority,
                    status = EXCLUDED.status,
                    member = EXCLUDED.member
                """,
                [
                    task_data.chat_id, 
                    task_data.subject, 
                    task_data.question, 
                    task_data.priority, 
                    task_data.status, 
                    task_data.member
                ]
            )
            await self.connection.commit()

    # Удалить запись из базы данных (любая таблица)
    async def delete(self, chat_id: int, table: DatabaseTable) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM %s WHERE chat_id = %s
                """,
                [table, chat_id]
            )
            await self.connection.commit()

    # Изменить статус запроса в таблице tasks
    async def set_task_status(self, chat_id: int, status: TaskStatus) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                UPDATE tasks SET status = %s WHERE chat_id = %s
                """,
                [status.value, chat_id]
            )

    # Изменить статус эксперта в таблице members
    async def set_member_status(self, chat_id: int, status: MemberStatus) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                UPDATE members SET status = %s WHERE chat_id = %s
                """,
                [status.value, chat_id]
            )
            await self.connection.commit()

    # Изменить предметы (столбец subjects) эксперта в таблице members
    async def set_member_subjects(self, chat_id: int, subjects: list[str]) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                UPDATE members SET subjects = %s WHERE chat_id = %s
                """,
                [subjects, chat_id]
            )
            await self.connection.commit()

    # Изменить роль пользователя в таблице users
    async def set_user_role(self, chat_id: int, role: UserRole) -> None:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                UPDATE users SET role = %s WHERE chat_id = %s
                """,
                [role.value, chat_id]
            )
            await self.connection.commit()

    # Найти chat_id пользователя по его имени/фамилии
    # TODO: Интегрировать cur.fetchmany(), добавить функцию для получения
    # количества доступных записей?
    async def search_users(self, realname: str) -> list[int]:
        async with self.connection.cursor() as cur:
            await cur.execute(
                """
                SELECT chat_id WHERE UPPER(realname) LIKE UPPER(%s)
                """,
                [f"%{realname}%"]
            )
            data = await cur.fetchall()
            if(data == None):
                raise UserNotFound(f"Unknown realname: {realname}")
            else:
                return data
            
    # Узнать, существует ли запись в базе данных (любая таблица)
    async def exists(self, chat_id: int, table: DatabaseTable) -> bool:
        async with self.connection.cursor() as cur:
            await cur.execute(
                sql.SQL("SELECT EXISTS(SELECT {table_name} WHERE chat_id = %s)")
                    .format(table_name = sql.Identifier(table.value)),
                [chat_id]
            )
            return await cur.fetchone()

    # Отключиться от базы данных    
    async def close(self) -> None:
        self.logger.info("Отключение от базы данных...")
        await self.connection.close()
        self.logger.info("База данных отключена.")