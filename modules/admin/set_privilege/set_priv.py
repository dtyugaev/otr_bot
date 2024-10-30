# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
import logging

from aiogram import types

from core import core_modules, resources, core_db

desc = {'supervisor': 'возможность просматривать все заявки',}

async def remove_privilege(message: types.Message):
    """
    Снятие прав пользователю

    :param message:
    :return:!
    """

    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')

        accept_priv = core_db.api.get_list_privileges()
        command = message.text.replace("/remove_priv", "").strip().split()

        if len(command) < 2:
            await message.answer("Используйте команду:\n/remove_priv <привилегия> <id пользователя>")
            return

        if not command[0] in accept_priv:
            _txt = f'Недопустимая привилегия "{command[0]}".\nДоступные привилегии:\n\n'
            for k,v in desc.items():
                _txt += f'-{k}\n{v}\n\n'

            await message.answer(_txt)
            return

        try:
            _id = int(command[1])
        except Exception:
            await message.answer("Используйте команду:\n/remove_priv <привилегия> <id пользователя>")
            return

        if not core_db.api.is_user_registered(_id):
            await message.answer(f"Пользователь {_id} не найден в базе данных. Используйте /list_users для просмотра списка зарегистрированных пользователей")
            return

        if core_db.api.update_privilege(tg_id=_id, what=command[0], new_value=0):
            await message.answer(f"Теперь {_id} не имеет {desc[command[0]]}")
            await resources.data.bot.send_message(chat_id=_id, text=f"Вам аннулировали привилегию {desc[command[0]]}")
        else:
            await message.answer("Ошибка обновления данных. Обратитесь к администратору")
            raise Exception("Error remove %s for %s" % (command[0], _id))
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка установки прав пользователю')

async def install_privilege(message: types.Message):
    """
    Установка прав пользователю

    :param message:
    :return:!
    """

    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')


        accept_priv = core_db.api.get_list_privileges()
        command = message.text.replace("/install_priv", "").strip().split()

        if len(command) < 2:
            await message.answer("Используйте команду:\n/install_priv <привилегия> <id пользователя>")
            return

        if not command[0] in accept_priv:
            _txt = f'Недопустимая привилегия "{command[0]}".\nДоступные привилегии:\n\n'
            for k,v in desc.items():
                _txt += f'-{k}\n{v}\n\n'

            await message.answer(_txt)
            return

        try:
            _id = int(command[1])
        except Exception:
            await message.answer("Используйте команду:\n/install_priv <привилегия> <id пользователя>")
            return

        if not core_db.api.is_user_registered(_id):
            await message.answer(f"Пользователь {_id} не найден в базе данных. Используйте /list_users для просмотра списка зарегистрированных пользователей")
            return

        if core_db.api.update_privilege(tg_id=_id, what=command[0], new_value=1):
            await message.answer(f"Теперь {_id} имеет {desc[command[0]]}")
            await resources.data.bot.send_message(chat_id=_id, text=f"Теперь Вам доступна {desc[command[0]]}")
        else:
            await message.answer("Ошибка обновления данных. Обратитесь к администратору")
            raise Exception("Error install %s for %s" % (command[0], _id))
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка установки прав пользователю')