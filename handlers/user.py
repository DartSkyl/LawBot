from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from routers import users_router
import keyboards as keys


@users_router.message(Command('start'))
async def start_func(msg: Message, state: FSMContext):
    """Начало начал"""
    await state.clear()
    await msg.answer("Добро пожаловать в юридический бот ⚖\nВыберите действие:",
                     reply_markup=keys.main_menu)
