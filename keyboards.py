from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


# ====================
# Общие клавиатуры
# ====================


main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⚖ Проверить организацию')],
    [KeyboardButton(text='📚 Законы и права')],
    [KeyboardButton(text='🆘 Жалоба / вопрос')]
], resize_keyboard=True)


async def sub_keys(channel_url):
    keys = InlineKeyboardBuilder()
    keys.button(text='Подписаться', url=channel_url)
    keys.button(text='Проверить', callback_data='start')
    keys.adjust(1)
    return keys.as_markup()


# ====================
# Для админов
# ====================

admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📥 Смотреть жалобы')],
    [KeyboardButton(text='💬 Ответить на жалобу')],
    [KeyboardButton(text='🗑 Удалить жалобу')]
], resize_keyboard=True)
