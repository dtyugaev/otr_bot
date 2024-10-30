# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types

"""

Генерация клавиатур для модуля операция по заявкам

"""


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
    cancel.row(types.KeyboardButton('Закончить работу с заявкой'))
    return cancel
