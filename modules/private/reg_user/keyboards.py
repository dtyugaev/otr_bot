# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types

"""

Генерация клавиатур для модуля регистрации

"""

def kb_recode():
    """
    Отправить код еще раз
    :return:
    """

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.row(types.InlineKeyboardButton('Отправить код ещё раз', callback_data='recode'))
    return kb




def kb_cancel():
    """
    Клавиатура для сброса регистрации
    :return:
    """
    cancel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    cancel.row(types.KeyboardButton('Отмена регистрации'))

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