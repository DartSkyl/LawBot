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


cancel_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отмена')]
], resize_keyboard=True)


# ====================
# Для админов
# ====================

admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📝 Карты потребителей')],
    [KeyboardButton(text='📕 Законы и права')],
    [KeyboardButton(text='📥 Жалобы / Вопросы')]
], resize_keyboard=True)

consumer_card_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📜 Текущие карты', callback_data='card_current')],
    [InlineKeyboardButton(text='➕ Добавить карту', callback_data='card_add')]
])


async def consumer_card_list(card_list: list):
    key = InlineKeyboardBuilder()
    for c in card_list:
        key.button(text=c['card_name'].replace('\\', ''), callback_data=f'card_show_{c["card_id"]}')
    key.adjust(1)
    return key.as_markup()


async def consumer_card_action(card_name: str, card_id: str, card_item_list: list):
    key = InlineKeyboardBuilder()
    key.button(text='➕ Добавить пункт', callback_data=f'card_add-item_{card_id}')
    for i in card_item_list:
        key.button(text=i['item_name'].replace('\\', ''), callback_data=f'item_show_{i["item_id"]}')
    key.button(text=f'Удалить "{card_name}"', callback_data=f'card_remove_{card_id}')
    key.adjust(1)
    return key.as_markup()


async def item_action(item):
    key = InlineKeyboardBuilder()
    key.button(text='Удалить пункт', callback_data=f'item_remove_{item["item_id"]}')
    key.button(text='⏪ Назад', callback_data=f'card_show_{item["card_id"]}')
    key.adjust(1)
    return key.as_markup()


confirm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Да', callback_data='yes')],
    [InlineKeyboardButton(text='🚫 Нет', callback_data='no')]
])

complaints_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📥 Смотреть жалобы/вопросы')],
    [KeyboardButton(text='💬 Ответить на жалобу/вопрос')],
    [KeyboardButton(text='🗑 Удалить жалобу/вопрос')]
], resize_keyboard=True)
