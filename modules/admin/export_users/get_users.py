# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

"""

Выгрузка пользователей в разные форматы

"""

import logging
import os

from aiogram import types

from core import core_modules, resources, core_db


async def hook(message: types.Message):
    """
    Получаем команду

    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
        users_file_path = await core_modules.generate_users_file()
        if not os.path.isfile(users_file_path):
            raise Exception("Not found %s" % users_file_path)

        await resources.data.bot.send_document(resources.data.config['Telegram']['approval_group_id'], types.InputFile(users_file_path))
        os.remove(users_file_path)
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'На этапе выгрузки списка зарегистрированных пользователей')
