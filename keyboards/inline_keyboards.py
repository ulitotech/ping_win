from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from math import ceil


class MenuCallBack(CallbackData, prefix="menu"):
    menu_name: str


class DeviceCallBack(CallbackData, prefix="device"):
    id: int


class PaginationCallBack(CallbackData, prefix="pagination"):
    command: str
    page: int


def get_callback_btns(*, btns: dict[str, str], sizes: tuple = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_devices_pagination(btns: dict[str, str], current_page: int):
    keyboard = InlineKeyboardBuilder()
    max_page = ceil(len(btns.items()) / 5)
    btns = {k: v for k, v in btns.items() if
            k in list(k for k in btns.keys())[(current_page - 1) * 5: current_page * 5]}
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=f"🔸 {text}", callback_data=DeviceCallBack(id=data).pack()))
    keyboard.add(InlineKeyboardButton(text=f'{"⏪" if current_page != 1 else "⏸"}',
                                      callback_data=PaginationCallBack(
                                          page=current_page - 1 if current_page != 1 else current_page,
                                          command='before' if current_page != 1 else 'now').pack()),
                 InlineKeyboardButton(text=fr'{current_page}/{max_page}', callback_data=PaginationCallBack(
                     page=current_page, command='now').pack()),
                 InlineKeyboardButton(text=f'{"⏩" if current_page < max_page else "⏸"}',
                                      callback_data=PaginationCallBack(
                                          page=current_page + 1 if current_page < max_page else current_page,
                                          command='next' if current_page < max_page else 'now').pack()),
                 InlineKeyboardButton(text='🆘 В списке нет устройства',
                                      callback_data=MenuCallBack(level=3, menu_name='support').pack()),
                 InlineKeyboardButton(text='💈 На главную',
                                      callback_data=MenuCallBack(level=1, menu_name='main').pack()), )
    return keyboard.adjust(*(1 for _ in range(len(btns))), 3, 1).as_markup()
