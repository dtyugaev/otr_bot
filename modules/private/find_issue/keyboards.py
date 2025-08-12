# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru


from aiogram import types
from core import resources

"""

Генерация клавиатур для модуля управления заявками

"""


def kb_processing_issue(data, isadmin=False):
    """
        Генерация клавиатуры для управления заявкой, относительно предоставляемой информации


    :param data: информация о заявке
    :param isadmin: Имеет ли доступ к заявке
    :return:
    """
    """
    
    1.	Если заявка не в статусе Закрыт или Решен: Добавить комментарий. 
    Появляется сообщение «Введите, пожалуйста, комментарий и прикрепите вложение.» После обновления заявки в JIRA пользователю выводится «Комментарий добавлен.» Комментарий и вложение добавляется в заявку.
    2.	Если заявка в статусе Запрос информации: Предоставить информацию. Появляется сообщение «Введите, пожалуйста, комментарий и прикрепите вложение.» После обновления заявки в JIRA пользователю выводится «Комментарий добавлен.». Выполняется переход в JIRA «Предоставить информацию». Прикладывается информация.
    3.	Если заявка в статусе Решен: Переоткрыть заявку. Появляется сообщение «Введите, пожалуйста, комментарий и прикрепите вложение.» После обновления заявки в JIRA пользователю выводится «Комментарий добавлен.» Выполняется переход в JIRA по переоткрытию заявки. Прикладывается информация.
    4.	Если заявка в статусе Решен: Подтвердить решение. Заявка в JIRA закрывается с комментарием. Пользователь получает «Заявка закрыта».

    """
    kb = types.InlineKeyboardMarkup(row_width=1)

    if data['Текущий статус'] not in ('Подтверждение решения', 'Закрыто', 'Запрос информации'):
        if isadmin:
            kb.row(types.InlineKeyboardButton(text="Добавить комментарий", callback_data='wait_comment:%s' % data['Номер заявки']))
    if data['Текущий статус'] == 'Запрос информации':
        if isadmin:
            kb.row(types.InlineKeyboardButton(text="Предоставить информацию", callback_data='give_info:%s' % data['Номер заявки']))
    if data['Текущий статус'] == 'Подтверждение решения':
        if isadmin:
            kb.row(types.InlineKeyboardButton(text="Переоткрыть заявку", callback_data='reopen_issue:%s' % data['Номер заявки']))
            kb.row(types.InlineKeyboardButton(text="Подтвердить решение", callback_data='accept_issue:%s' % data['Номер заявки']))

    if data['Количество вложений'] > 0:
        kb.row(types.InlineKeyboardButton(text="Получить вложения", callback_data='get_attach:%s' % data['Номер заявки']))

    kb.row(types.InlineKeyboardButton(text="Открыть заявку на портале", url=f"{resources.data.config['jira']['url']}/servicedesk/customer/portal/6/{data['Номер заявки']}"))
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
    cancel.row(types.KeyboardButton('Отмена'))
    return cancel
