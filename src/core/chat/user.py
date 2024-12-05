# Подключение модулей библиотеки aiogram
from aiogram import types, F
from aiogram import Router, Bot
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext

# Подключение core-библиотек
from core.db.connector import DatabaseConnector

# Инициализация Router'а для обычных пользователей
router_user = Router()