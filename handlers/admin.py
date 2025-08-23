import string
from random import choices

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from asyncpg.exceptions import UniqueViolationError

from routers import admin_router
import keyboards as keys
from states import Admin
from loader import base


@admin_router.message(Command('admin'))
async def open_admin_panel(msg: Message, state: FSMContext):
    """Открываем админ панель"""
    await state.clear()
    await msg.answer("🛠 Админ-панель", reply_markup=keys.admin_menu)


# ====================
# Карты потребителей
# ====================


async def open_card(msg: Message, card_id: str):
    """Открываем карту потребителя"""
    card = await base.get_card_by_id(card_id)
    card_item = await base.get_all_items_by_card(card_id)
    msg_text = f'*_{card["card_name"]}:_*\n\n{card["card_content"]}'
    await msg.answer(msg_text,
                     reply_markup=await keys.consumer_card_action(
                         card['card_name'],
                         card['card_id'],
                         card_item
                     ),
                     parse_mode='MarkdownV2')


@admin_router.message(F.text == '📝 Карты потребителей')
async def consumer_card_menu(msg: Message):
    """Меню действий с картами потребителей"""
    await msg.answer('Выберете действие:', reply_markup=keys.consumer_card_menu)


@admin_router.callback_query(F.data.startswith('card_'))
async def catch_card_action(callback: CallbackQuery, state: FSMContext):
    """Ловим действие по картам"""
    await callback.message.delete()

    # Вывод списка текущих карт
    if callback.data == 'card_current':
        card_list = await base.get_all_cards()
        await callback.message.answer('Выберете карту потребителя:',
                                      reply_markup=await keys.consumer_card_list(card_list))

    # Вывод конкретной карты
    elif callback.data.startswith('card_show_'):
        await open_card(callback.message, callback.data.removeprefix('card_show_'))

    # Добавление новой карты
    elif callback.data == 'card_add':

        await state.set_state(Admin.add_new_card_name)
        await callback.message.answer('Введите название новой карты:', reply_markup=keys.cancel_button)

    # Добавление нового пункта к карте
    elif callback.data.startswith('card_add-item_'):

        await state.set_state(Admin.add_new_card_item_name)

        # И сразу сохраним ID карты куда добавляем пункт
        await state.set_data({'card_id': callback.data.removeprefix('card_add-item_')})
        await callback.message.answer('Введите название пункта:', reply_markup=keys.cancel_button)

    # Удаление карты
    else:
        await state.set_state(Admin.remove_card)
        await state.set_data({'card_id_for_remove': callback.data.removeprefix('card_remove_')})
        await callback.message.answer('Вы уверены?', reply_markup=keys.confirm)


async def open_item(msg: Message, item_id: str):
    """Открываем конкретный пункт"""
    item = await base.get_item_by_id(item_id)
    msg_text = f'*_{item["item_name"]}:_*\n\n{item["item_content"]}'
    await msg.answer(msg_text, reply_markup=await keys.item_action(item), parse_mode='MarkdownV2')


@admin_router.callback_query(F.data.startswith('item_'))
async def show_item(callback: CallbackQuery, state: FSMContext):
    """Открываем конкретный пункт карты"""
    await callback.message.delete()

    # Открываем пункт
    if callback.data.startswith('item_show_'):
        await open_item(callback.message, callback.data.removeprefix('item_show_'))

    # Удаляем пункт и открываем карту
    elif callback.data.startswith('item_remove_'):

        await state.set_state(Admin.remove_item)
        await state.set_data({'item_for_remove_id': callback.data.removeprefix('item_remove_')})
        await callback.message.answer('Вы уверены?', reply_markup=keys.confirm)


@admin_router.callback_query(Admin.remove_card, F.data.in_(['yes', 'no']))
async def card_remove_confirm(callback: CallbackQuery, state: FSMContext):
    """Ловим подтверждение удаления карты"""
    await callback.message.delete()
    card_for_remove_id = (await state.get_data())['card_id_for_remove']
    await state.clear()
    if callback.data == 'yes':
        await base.remove_card(card_for_remove_id)
        await callback.message.answer('Карта удалена')
        await callback.message.answer('Выберете действие:', reply_markup=keys.consumer_card_menu)
    else:
        await open_card(callback.message, card_for_remove_id)


@admin_router.callback_query(Admin.remove_item, F.data.in_(['yes', 'no']))
async def item_remove_confirm(callback: CallbackQuery, state: FSMContext):
    """Ловим подтверждение удаления пункта"""
    await callback.message.delete()
    item_for_remove_id = (await state.get_data())['item_for_remove_id']
    await state.clear()
    if callback.data == 'yes':
        item_for_remove = await base.get_item_by_id(item_for_remove_id)
        await base.remove_item(item_for_remove_id)
        await callback.message.answer('Пункт удален')
        await open_card(callback.message, item_for_remove['card_id'])
    else:
        await open_item(callback.message, item_for_remove_id)


@admin_router.message(Admin.add_new_card_name, F.text != 'Отмена')
async def catch_name_for_new_card(msg: Message, state: FSMContext):
    """Ловим название новой карты"""
    await state.set_data({'card_name': msg.md_text})
    await state.set_state(Admin.add_new_card_content)
    await msg.answer('Теперь введите описание карты:')


@admin_router.message(Admin.add_new_card_content, F.text != 'Отмена')
async def catch_content_for_new_card(msg: Message, state: FSMContext):
    """Ловим содержимое для новой карты"""
    new_card_id = ''.join(choices(string.digits + string.ascii_letters, k=8))
    try:
        await base.add_new_card(
            card_name=(await state.get_data())['card_name'],
            card_id=new_card_id,
            card_content=msg.md_text
        )
        await state.clear()
        await msg.answer('Карта сохранена', reply_markup=keys.admin_menu)
        await open_card(msg, new_card_id)
    except UniqueViolationError:
        await state.clear()
        await msg.answer('Карта с таким названием уже существует!', reply_markup=keys.admin_menu)


@admin_router.message(Admin.add_new_card_item_name, F.text != 'Отмена')
async def catch_name_for_new_item(msg: Message, state: FSMContext):
    """Ловим название для нового пункта"""
    await state.update_data({'item_name': msg.md_text})
    await state.set_state(Admin.add_new_card_item_content)
    await msg.answer('Теперь введите содержимое пункта:')


@admin_router.message(Admin.add_new_card_item_content, F.text != 'Отмена')
async def catch_content_for_new_item(msg: Message, state: FSMContext):
    """Ловим содержимое для нового пункта"""
    new_item_id = ''.join(choices(string.digits + string.ascii_letters, k=8))
    item_data = await state.get_data()
    await base.add_new_item(
        item_name=item_data['item_name'],
        item_id=new_item_id,
        item_content=msg.md_text,
        card_id=item_data['card_id']
    )
    await state.clear()
    await msg.answer('Пункт сохранен', reply_markup=keys.admin_menu)
    await open_card(msg, item_data['card_id'])


@admin_router.message(F.text == 'Отмена')
async def cancel_func(msg: Message, state: FSMContext):
    """Отмена"""
    await state.clear()
    await msg.answer('Действие отменено', reply_markup=keys.admin_menu)
