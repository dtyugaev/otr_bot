# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types

"""

Генерация клавиатур для модуля работы с заявками

"""


def kb_find_issue():
    """
    Клавиатура для поиска заявки по номеру
    :return:
    """
    kb = types.InlineKeyboardMarkup(row_width=1)
    find = types.InlineKeyboardButton(text="Найти заявку по номеру", callback_data='find_issue')
    kb.row(find)
    return kb

def kb_main():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.row(types.InlineKeyboardButton('Список моих заявок', callback_data='list_my_issue'))
    kb.row(types.InlineKeyboardButton('Найти заявку по номеру', callback_data='find_issue_number'))
    return kb
