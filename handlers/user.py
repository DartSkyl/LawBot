from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from routers import users_router
import keyboards as keys
from loader import base


@users_router.message(Command('start'))
async def start_func(msg: Message, state: FSMContext):
    """Начало начал"""
    await state.clear()
    await msg.answer("Добро пожаловать в юридический бот ⚖\nВыберите действие:",
                     reply_markup=keys.main_menu)


@users_router.callback_query(F.data == 'open_card_list')
async def open_card_list(callback: CallbackQuery):
    """Открываем список карт потребителя"""
    await callback.message.delete()
    card_list = await base.get_all_cards()
    await callback.message.answer('Выберете карту потребителя:',
                                  reply_markup=await keys.consumer_card_list_for_user(card_list))


@users_router.message(F.text == '⚖ Проверить организацию')
async def open_card_list(msg: Message):
    """Открываем список карт потребителя"""
    card_list = await base.get_all_cards()
    await msg.answer('Выберете карту потребителя:',
                     reply_markup=await keys.consumer_card_list_for_user(card_list))


async def open_card_user(msg: Message, card_id: str):
    """Открываем карту потребителя"""
    card = await base.get_card_by_id(card_id)
    card_item = await base.get_all_items_by_card(card_id)
    msg_text = f'*_{card["card_name"]}:_*\n\n{card["card_content"]}'
    await msg.answer(msg_text,
                     reply_markup=await keys.consumer_card_items(card_item),
                     parse_mode='MarkdownV2')


async def open_item_user(msg: Message, item_id: str):
    """Открываем конкретный пункт"""
    item = await base.get_item_by_id(item_id)
    msg_text = f'*_{item["item_name"]}:_*\n\n{item["item_content"]}'
    await msg.answer(msg_text, reply_markup=await keys.item_back(item['card_id']), parse_mode='MarkdownV2')


@users_router.callback_query(F.data.startswith('u_card_view_'))
async def open_card(callback: CallbackQuery):
    """Открываем карту потребителя"""
    await callback.message.delete()
    await open_card_user(callback.message, callback.data.removeprefix('u_card_view_'))


@users_router.callback_query(F.data.startswith('u_item_view_'))
async def open_item(callback: CallbackQuery):
    """Открываем пункт карты потребителя"""
    await callback.message.delete()
    await open_item_user(callback.message, callback.data.removeprefix('u_item_view_'))


@users_router.message(F.text == '📚 Законы и права')
async def open_law_list(msg: Message):
    """Открываем список законов"""
    law_list = await base.get_all_laws()
    msg_text = 'Доступные законы/права для ознакомления:\n\n'
    for la in law_list:
        msg_text += f'*_{la["law_name"]} \-_* _{la["law_description"]}_\n\n'
    await msg.answer(msg_text, reply_markup=await keys.law_list_user(law_list), parse_mode='MarkdownV2')


@users_router.callback_query(F.data == 'open_law_list')
async def open_law_list(callback: CallbackQuery):
    """Открываем список законов"""
    await callback.message.delete()
    law_list = await base.get_all_laws()
    msg_text = 'Доступные законы/права для ознакомления:\n\n'
    for la in law_list:
        msg_text += f'*_{la["law_name"]} \-_* _{la["law_description"]}_\n\n'
    await callback.message.answer(msg_text,
                                  reply_markup=await keys.law_list_user(law_list),
                                  parse_mode='MarkdownV2')


@users_router.callback_query(F.data.startswith('u_law_view_'))
async def open_law(callback: CallbackQuery):
    """Открываем закон"""
    await callback.message.delete()
    law = await base.get_law_by_id(callback.data.removeprefix('u_law_view_'))
    msg_text = f'*_{law["law_name"]}:_*\n\n{law["law_content"]}'
    await callback.message.answer(msg_text, reply_markup=keys.law_back, parse_mode='MarkdownV2')
