# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
import datetime
import json
import logging

from aiogram import types

from core import core_modules, constant, core_db


async def get_status(message: types.Message):
    """
    Отправляем информацию по работе бота командой /status

    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
        with open(constant.STATUS_FILE, 'r') as file:
            status = json.load(file)

        time_left = int((datetime.datetime.now() - datetime.datetime.strptime(status['time_start'], "%d/%m/%Y %H:%M:%S")).seconds / 60)
        await message.answer("Версия: {}\nВремя старта: {} ({} мин.)".format(status['ver'], status['time_start'], time_left))
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка вывода статуса работы')