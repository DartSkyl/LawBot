from random import choice

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext

from utils.routers import users_router
import keyboards as keys
from config import ADMINS
from loader import base


@users_router.message(Command('start'))
async def start_func(msg: Message, state: FSMContext):
    """Начало начал"""
    await state.clear()
    await msg.answer("Добро пожаловать в юридический бот ⚖\nВыберите действие:",
                     reply_markup=keys.main_menu)
