# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru


from aiogram import types

from core import core_modules, core_db


async def get_logs(message: types.Message):
    """
    Получаем все логи с сервера и отправляем их в чат админов

    :return:
    """
    core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
    await core_modules.send_logs()