from aiogram.fsm.state import StatesGroup, State


class Admin(StatesGroup):
    add_new_card_name = State()
    add_new_card_content = State()

    add_new_card_item_name = State()
    add_new_card_item_content = State()

    remove_card = State()
    remove_item = State()

