# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru


from aiogram import types
from aiogram.utils.callback_data import CallbackData

"""

Генерация клавиатур для модуля Мой профиль

"""

def kb_menu():
    """
    Клавиатура для выбора между удалением и редактированием
    :return:
    """
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.row(types.InlineKeyboardButton(text="Удалить профиль", callback_data='prof:del'))
    return kb

def kb_yes_or_not():
    """
    да или нет

    :return:
    """
    verd_cb = CallbackData('prof', 'aprove')
    kb = types.InlineKeyboardMarkup(row_width=1)
    _true = types.InlineKeyboardButton('Подтвердить', callback_data=verd_cb.new(aprove=True))
    _false = types.InlineKeyboardButton('Отменить', callback_data=verd_cb.new(aprove=False))
    kb.row(_false, _true)
    return kb

def kb_cancel():
    """
    Кнопка отмены
    :return:
    """
    cancel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    cancel.row(types.KeyboardButton('Завершить работу с профилем'))
    return cancel

def generate_startup_menu():
    """
    Генерация стартовых кнопок

    :return:
    """
    startup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    startup.row(types.KeyboardButton('Создать заявку'), types.KeyboardButton('Узнать статус заявки'))
    startup.row(types.KeyboardButton('Мой профиль'), types.KeyboardButton('Обратная связь'))
    return startup