# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types

"""

Генерация клавиатур для стартового модуля

"""


def kb_my_profile():
    """
    Клавиатура для 'мой профиль'
    :return:
    """
    prof = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    prof.row(types.KeyboardButton('Мой профиль'))
    return prof


def kb_create_issue():
    """
    Клавиатура для 'создать заявку'
    :return:
    """
    c_issue = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    c_issue.row(types.KeyboardButton('Создать заявку'))
    return c_issue


def kb_feedback():
    """
    Клавиатура для 'Обратная связь'
    :return:
    """
    feedback = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    feedback.row(types.KeyboardButton('Обратная связь'))
    return feedback


def kb_status_issue():
    """
    Клавиатура для 'Узнать статус заявки'
    :return:
    """
    status_issue = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    status_issue.row(types.KeyboardButton('Узнать статус заявки'))
    return status_issue


def generate_startup_menu():
    """
    Генерация стартовых кнопок

    :return:
    """
    startup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    startup.row(types.KeyboardButton('Создать заявку'), types.KeyboardButton('Узнать статус заявки'))
    startup.row(types.KeyboardButton('Мой профиль'), types.KeyboardButton('Обратная связь'))
    return startup
