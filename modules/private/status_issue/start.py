# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
import logging

from aiogram import types

from core import core_modules, resources
from . import keyboards

"""
Модуль, который реагирует на команду кнопку 'Список заявок'

"""


async def generate_choise(message: types.Message):
    """
    Генерация дополнительных кнопок

    :param message:
    :return:
    """
    try:
        await message.answer('Что требуется?', reply_markup=keyboards.kb_main())
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка кнопки "статус заявок"')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')

