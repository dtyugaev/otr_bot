# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types
from aiogram.utils.callback_data import CallbackData

"""

Генерация клавиатур для модуля обратной связи

"""


def kb_answer_feedback(issue, id_user):
    """
    Клавиатура для ответа на фитбек
    :return:
    """
    kb = types.InlineKeyboardMarkup(row_width=1)
    cb = CallbackData("fb_answer", "id_issue", "id_user")
    answer = types.InlineKeyboardButton(text="Ответить", callback_data=cb.new(id_issue=issue, id_user=id_user))
    kb.row(answer)
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
    cancel.row(types.KeyboardButton('Отменить обращение'))
    return cancel