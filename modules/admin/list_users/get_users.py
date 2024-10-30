# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru


"""
Вывод списка пользователей в админский чат

"""
import logging

from aiogram import types

from core import core_modules, resources, core_db


async def get_all_users(message: types.Message):
    """
    Отправляем в админский чат список всех пользователей

    :param message:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')

        def _pattern_check(data, pattern):
            for kk, vv in data.items():
                for kkk, vvv in vv.items():
                    if pattern.lower() in str(vvv).lower() or pattern in str(kk):
                        return True
            return False


        command = message.text.split()
        pattern = ''
        if len(command) >= 2:
            pattern = ' '.join(command[1:])
        else:
            await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], 'Задайте критерий поиска. Например\n\n/list_users 1234567890')
            return

        users = core_db.api.get_all_user_profile()

        text = ''
        c = 0
        for k, v in users.items():
            if pattern:
                if not _pattern_check({k: v}, pattern):
                    continue

            text += f"id: {k}\n" \
                f"ФИО: {v['fio']}\n" \
                f"Email: {v['email']}\n" \
                f"{'Имеет доступ к просмотру всех заявок (supervisor)' if v['privilege']['supervisor'] == 1 else 'Нет доступа к просмотру всех заявок (supervisor)'}\n\n"

            c += 1
            if c == 5:
                await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], text)
                c = 0
                text = ''

        if text:
            await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], text)
        else:
            await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], "Данных не найдено")

    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'На этапе формирования списка зарегистрированных пользователей')
