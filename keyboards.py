from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup


# ====================
# Общие клавиатуры
# ====================


main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⚖ Проверить организацию')],
    [KeyboardButton(text='📚 Законы и права')],
    [KeyboardButton(text='🆘 Жалоба / вопрос')]
], resize_keyboard=True)


async def consumer_card_list_for_user(card_list: list):
    key = InlineKeyboardBuilder()
    for c in card_list:
        key.button(text=c['card_name'].replace('\\', ''), callback_data=f'u_card_view_{c["card_id"]}')
    key.adjust(1)
    return key.as_markup()


async def consumer_card_items(card_item_list: list):
    key = InlineKeyboardBuilder()
    for i in card_item_list:
        key.button(text=i['item_name'].replace('\\', ''), callback_data=f'u_item_view_{i["item_id"]}')
    key.button(text='⏪ Назад', callback_data=f'open_card_list')
    key.adjust(1)
    return key.as_markup()


async def item_back(card_id):
    key = InlineKeyboardBuilder()
    key.button(text='⏪ Назад', callback_data=f'u_card_view_{card_id}')
    key.adjust(1)
    return key.as_markup()


async def law_list_user(laws: list):
    keys = InlineKeyboardBuilder()
    for la in laws:
        keys.button(text=la['law_name'].replace('\\', ''), callback_data=f'u_law_view_{la["law_id"]}')
    keys.adjust(1)
    return keys.as_markup()

law_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⏪ Назад', callback_data='open_law_list')]
])


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
    [KeyboardButton(text='📝 Карты потребителей'), KeyboardButton(text='📕 Законы и права')],
    [KeyboardButton(text='📥 Жалобы / Вопросы')]
], resize_keyboard=True)

consumer_card_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📜 Текущие карты', callback_data='card_current')],
    [InlineKeyboardButton(text='➕ Добавить карту', callback_data='card_add')]
])

law_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📜 Текущие законы и права', callback_data='law_current')],
    [InlineKeyboardButton(text='➕ Добавить закон или право', callback_data='law_add')]
])


async def law_action(law_name: str, law_id: str):
    keys = InlineKeyboardBuilder()
    law_name = law_name.replace('\\', '')
    keys.button(text=f'Удалить "{law_name}"', callback_data=f'law_remove_{law_id}')
    keys.button(text='⏪ Назад', callback_data='law_current')
    keys.adjust(1)
    return keys.as_markup()


async def law_list(laws: list):
    keys = InlineKeyboardBuilder()
    for la in laws:
        keys.button(text=la['law_name'].replace('\\', ''), callback_data=f'law_show_{la["law_id"]}')
    keys.adjust(1)
    return keys.as_markup()


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
    card_name = card_name.replace('\\', '')
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
