# -*- coding: utf-8 -*-
# Edit by Kochetkov Artem
# skype: artemk_85
# mail: kochetkov.artem@otr.ru
#


import html

from aiogram import types

def generate_startup_menu():
    """
    Генерация стартовых кнопок

    :return:
    """
    startup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    startup.row(types.KeyboardButton('Создать заявку'), types.KeyboardButton('Узнать статус заявки'))
    startup.row(types.KeyboardButton('Мой профиль'), types.KeyboardButton('Обратная связь'))
    return startup

def kb_generate_issue_button(issues: list, page_number: int):
    kb = types.InlineKeyboardMarkup(row_width=1)

    """
    IT-00000 | Статус | Тема | 
    """
    for i in issues[page_number]:
        title = f"{i.key} | {i.fields.status.name} | {html.escape(i.fields.summary)}"
        kb.row(types.InlineKeyboardButton(title, callback_data=f'issue:{i.key}:{page_number}'))

    if len(issues) == 1:
        kb.row(types.InlineKeyboardButton('◀', callback_data=f'issue:page:null:{page_number}'), types.InlineKeyboardButton(f'{page_number + 1} из {len(issues)}', callback_data=f'issue:page:null:{page_number}'), types.InlineKeyboardButton('▶', callback_data=f'issue:page:null:{page_number}'))
    elif page_number == 0:
        kb.row(types.InlineKeyboardButton('◀', callback_data=f'issue:page:null:{page_number}'), types.InlineKeyboardButton(f'{page_number + 1} из {len(issues)}', callback_data=f'issue:page:null:{page_number}'), types.InlineKeyboardButton('▶', callback_data=f'issue:page:null:next:{page_number}'))
    elif page_number + 1 == len(issues):
        kb.row(types.InlineKeyboardButton('◀', callback_data=f'issue:page:null:prev:{page_number}'), types.InlineKeyboardButton(f'{page_number + 1} из {len(issues)}', callback_data=f'issue:page:null:{page_number}'), types.InlineKeyboardButton('▶', callback_data=f'issue:page:null:{page_number}'))
    else:
        kb.row(types.InlineKeyboardButton('◀', callback_data=f'issue:page:null:prev:{page_number}'), types.InlineKeyboardButton(f'{page_number + 1} из {len(issues)}', callback_data=f'issue:page:null:{page_number}'), types.InlineKeyboardButton('▶', callback_data=f'issue:page:null:next:{page_number}'))
    return kb
