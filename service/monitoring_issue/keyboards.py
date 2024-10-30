# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
from aiogram import types

"""

Генерация клавиатур для модуля мониторинга заявок

"""


def kb_open_issue(issue_id):
    """
    Клавиатура для быстрого открытия заявки
    :return:
    """
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.row(types.InlineKeyboardButton(text="Открыть заявку", callback_data=f'open_i_m:{issue_id}'))
    return kb