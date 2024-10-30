# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
from aiogram import types

from core import core_db
from . import keyboards

"""
Модуль, который реагирует на команду /start в личных сообщениях

"""

async def cmd_start(message: types.Message):
    """
    Модуль, который посылает ответ в чат, на команду '/start'

    :param message:
    :return:
    """
    core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
    if not core_db.api.is_user_approved(message.from_user.id):
        await message.reply('Добрый день! Вас приветствует бот Службы технической поддержки. Для создания профиля и начала использования бота нажмите /regme', reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.reply('Доброго дня!', reply_markup=keyboards.generate_startup_menu())
