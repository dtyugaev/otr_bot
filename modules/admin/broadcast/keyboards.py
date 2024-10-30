# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
from aiogram import types
from aiogram.utils.callback_data import CallbackData

"""

Генерация клавиатур для модуля отправки сообщений от бота

"""


def kb_accept_send():
    """
    Клавиатура для подтверждения отправки письма пользователю
    :return:
    """
    kb = types.InlineKeyboardMarkup(row_width=1)
    cb = CallbackData("accept_send", "action")
    accept = types.InlineKeyboardButton(text="✅", callback_data=cb.new(action='yes'))
    not_accept = types.InlineKeyboardButton(text="❌", callback_data=cb.new(action='no'))
    kb.row(not_accept, accept)
    return kb