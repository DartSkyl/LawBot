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
from loader import base, bot


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
    elif callback.data.startswith('card_remove_'):
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


# ====================
# Законы и права
# ====================


@admin_router.message(F.text == '📕 Законы и права')
async def open_law_menu(msg: Message):
    """Открываем меню закона и права"""
    await msg.answer('Выберете действие:', reply_markup=keys.law_menu)


async def open_law(msg: Message, law_id: str):
    """Открываем конкретный закон"""
    law = await base.get_law_by_id(law_id)
    msg_text = f'*_{law["law_name"]}:_*\n\nОписание \- _{law["law_description"]}_\n\n{law["law_content"]}'
    await msg.answer(msg_text,
                     reply_markup=await keys.law_action(law['law_name'], law['law_id']),
                     parse_mode='MarkdownV2')


@admin_router.callback_query(F.data.startswith('law_'))
async def catch_law_action(callback: CallbackQuery, state: FSMContext):
    """Ловим действие с законом"""
    await callback.message.delete()

    # Список текущих законов
    if callback.data == 'law_current':

        law_list = await base.get_all_laws()
        await callback.message.answer('Выберете закон/право:',
                                      reply_markup=await keys.law_list(law_list))

    # Открываем конкретный закон
    elif callback.data.startswith('law_show_'):

        await open_law(callback.message, callback.data.removeprefix('law_show_'))

    # Добавляем новый закон
    elif callback.data == 'law_add':

        await state.set_state(Admin.add_new_law_name)
        await callback.message.answer('Введите название закона или права:', reply_markup=keys.cancel_button)

    # Удаляем закон
    elif callback.data.startswith('law_remove_'):

        await state.set_state(Admin.remove_law)
        await state.set_data({'law_for_remove_id': callback.data.removeprefix('law_remove_')})
        await callback.message.answer('Вы уверены?', reply_markup=keys.confirm)


@admin_router.message(Admin.add_new_law_name, F.text != 'Отмена')
async def catch_name_new_law(msg: Message, state: FSMContext):
    """Ловим название нового закона"""
    await state.set_data({'law_name': msg.md_text})
    await state.set_state(Admin.add_new_law_description)
    await msg.answer('Теперь введите описание:')


@admin_router.message(Admin.add_new_law_description, F.text != 'Отмена')
async def catch_description_new_law(msg: Message, state: FSMContext):
    """Ловим описание нового закона"""
    await state.update_data({'law_description': msg.md_text})
    await state.set_state(Admin.add_new_law_content)
    await msg.answer('Теперь сам закон или право:')


@admin_router.message(Admin.add_new_law_content, F.text != 'Отмена')
async def catch_content_new_law(msg: Message, state: FSMContext):
    """Ловим содержание нового закона"""
    law_data = await state.get_data()
    new_law_id = ''.join(choices(string.digits + string.ascii_letters, k=8))
    await base.add_new_law(
        law_name=law_data['law_name'],
        law_id=new_law_id,
        law_description=law_data['law_description'],
        law_content=msg.md_text
    )
    await state.clear()
    await msg.answer('Закон/право сохранено', reply_markup=keys.admin_menu)
    await open_law(msg, new_law_id)


@admin_router.callback_query(Admin.remove_law, F.data.in_(['yes', 'no']))
async def law_remove_confirm(callback: CallbackQuery, state: FSMContext):
    """Ловим подтверждение удаления закона"""
    await callback.message.delete()
    law_for_remove_id = (await state.get_data())['law_for_remove_id']
    await state.clear()
    if callback.data == 'yes':
        await base.remove_law(law_for_remove_id)
        await callback.message.answer('Закон/право удален', reply_markup=keys.admin_menu)
        await callback.message.answer('Выберете действие:', reply_markup=keys.law_menu)
    else:
        await open_law(callback.message, law_for_remove_id)


# ====================
# Обращения
# ====================


@admin_router.message(F.text == '📥 Жалобы / Вопросы')
async def get_complaints_list(msg: Message):
    """Выдаем список всех обращений"""
    complaints_list = await base.get_all_complaint()
    for c in complaints_list:
        msg_text = (f'Вопрос/жалоба № <b>{c["id"]}</b>\n'
                    f'От пользователя @{c["username"]}\n'
                    f'{"❗Ожидает ответ❗" if not c["answer_status"] else "✅ Обработано"}\n\n'
                    f'{c["text"]}')
        await msg.answer(msg_text, reply_markup=await keys.complaint_action(
            c["id"],
            c["answer_status"]
        ))


@admin_router.callback_query(F.data.startswith('complaint_answer_'))
async def start_complaint_answer(callback: CallbackQuery, state: FSMContext):
    """Начинаем писать ответ на обращение"""
    await callback.message.delete()
    complaint_for_answer_id = int(callback.data.removeprefix('complaint_answer_'))
    complaint = await base.get_complaint_by_id(complaint_for_answer_id)
    msg_text = (f'Ответ на вопрос/жалобу № <b>{complaint["id"]}</b>\n'
                f'Для пользователя @{complaint["username"]}\n\n'
                f'Введите текст ответа:')
    await state.set_data({'complaint_for_answer_id': complaint_for_answer_id})
    await state.set_state(Admin.complaint_answer)
    await callback.message.answer(msg_text, reply_markup=keys.cancel_button)


@admin_router.message(Admin.complaint_answer, F.text != 'Отмена')
async def catch_complaint_answer(msg: Message, state: FSMContext):
    """Ловим ответ на обращение"""
    complaint_for_answer_id = (await state.get_data())['complaint_for_answer_id']
    await state.clear()
    complaint = await base.get_complaint_by_id(complaint_for_answer_id)
    msg_text = (f'Уважаемый пользователь! Вот ответ на ваш вопрос/жалобу № <b>{complaint["id"]}</b>:\n\n'
                f'{msg.text}\n\nС уважением, администрация')
    await bot.send_message(complaint['user_id'], msg_text)
    await base.change_answer_status(complaint_for_answer_id, 'true')
    await msg.answer('Отправлено 📩', reply_markup=keys.admin_menu)
    msg_text = f'Ответ на вопрос/жалобу № <b>{complaint["id"]}</b> для пользователя @{complaint["username"]} доставлен'
    await msg.answer(msg_text, reply_markup=await keys.complaint_action(complaint["id"], True))


@admin_router.callback_query(F.data.startswith('complaint_remove_'))
async def start_complaint_remove(callback: CallbackQuery, state: FSMContext):
    """Начинаем удаление обращения"""
    await callback.message.delete()
    await state.set_state(Admin.remove_complaint)
    await state.set_data({'complaint_for_remove_id': int(callback.data.removeprefix('complaint_remove_'))})
    await callback.message.answer('Вы уверены?', reply_markup=keys.confirm)


@admin_router.callback_query(Admin.remove_complaint, F.data.in_(['yes', 'no']))
async def confirm_complaint_remove(callback: CallbackQuery, state: FSMContext):
    """Ловим подтверждение удаления обращения"""
    complaint_for_remove_id = (await state.get_data())['complaint_for_remove_id']
    await state.clear()
    await callback.message.delete()
    if callback.data == 'yes':
        await base.remove_complaint(complaint_for_remove_id)
        await callback.message.answer('Обращение удалено', reply_markup=keys.admin_menu)
    else:
        complaint = await base.get_complaint_by_id(complaint_for_remove_id)
        msg_text = (f'Вопрос/жалоба № <b>{complaint["id"]}</b>\n'
                    f'От пользователя @{complaint["username"]}\n'
                    f'{"❗Ожидает ответ❗" if not complaint["answer_status"] else "✅ Обработано"}\n\n'
                    f'{complaint["text"]}')
        await callback.message.answer(msg_text, reply_markup=await keys.complaint_action(
            complaint["id"],
            complaint["answer_status"]
        ))


@admin_router.message(F.text == 'Отмена')
async def cancel_func(msg: Message, state: FSMContext):
    """Отмена"""
    await state.clear()
    await msg.answer('Действие отменено', reply_markup=keys.admin_menu)


@admin_router.message(Command('help'))
async def help_msg(msg: Message):
    with open('help.txt', 'r', encoding='UTF-8') as file:
        msg_text = file.read()
        await msg.answer(msg_text)
