# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types
from aiogram.utils.callback_data import CallbackData

"""

Генерация клавиатур для модуля создания заявки

"""

def kb_accept_create():
    """
    Клавиатура для подтверждения создания заявки
    :return:
    """
    kb = types.InlineKeyboardMarkup(row_width=1)
    cb = CallbackData("accept_create_issue", "action")
    accept = types.InlineKeyboardButton(text="Подтвердить", callback_data=cb.new(action='yes'))
    not_accept = types.InlineKeyboardButton(text="Отменить", callback_data=cb.new(action='no'))
    kb.row(not_accept, accept)
    return kb

def generate_startup_menu():
    """
    Генерация стартовых кнопок

    :return:
    """
    startup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    startup.row(types.KeyboardButton('Создать заявку'), types.KeyboardButton('Узнать статус заявки'))
    startup.row(types.KeyboardButton('Мой профиль'), types.KeyboardButton('Обратная связь'))
    return startup

def kb_cancel():
    """
    Кнопка отмены
    :return:
    """
    cancel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    cancel.row(types.KeyboardButton('Отменить создание заявки'))
    return cancel
