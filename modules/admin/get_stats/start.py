# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru


"""
Модуль для сбора статистики
"""

import logging

from aiogram import types

from core import core_modules, resources, core_db


async def get_all_stats(message: types.Message):
    """
    Отправляем в админский чат запрошенную статистику

    :param message:
    :return:
    """
    try:
        accept_stat = ('day', 'week', 'month', 'all',)


        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
        command = message.text.split()
        if len(command) < 2:
            await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], 'Задайте срез\n\nНапример статистика за текущий день:\n/stat day')
            return
        srez = command[1]

        if srez not in accept_stat:
            await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], f'Доступные срезы:\n\n{", ".join(accept_stat)}')
            return

        res = core_db.api.get_stats(srez)

        if not res:
            await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], 'Статистики за указанный период нет')
            return

        data = {'Открыть заявку': list(),
                'Создание заявки': list(),
                'Добавить комментарий в заявку': list(),
                'Изменить статус заявки': list(),
                'Неизвестная статистика': list()}

        for i in res:
            action = i['action']
            if action not in data.keys():
                data['Неизвестная статистика'].append(i)
            else:
                data[action].append(i)

        if srez == 'day':
            s_t = 'текущий день'
        elif srez == 'week':
            s_t = 'последние 7 дней'
        elif srez == 'month':
            s_t = 'последние 30 дней'
        elif srez == 'all':
            s_t = 'все время'
        else:
            s_t = srez

        text = f'Статистика за {s_t}\n\n'
        for k, v in data.items():
            if k == 'Открыть заявку':
                text += f'Всего просмотров заявок: {len(v)}\n'
            elif k == 'Создание заявки':
                text += f'Всего созданных заявок: {len(v)}\n'
            elif k == 'Добавить комментарий в заявку':
                text += f'Всего добавленных комментариев: {len(v)}\n'
            elif k == 'Изменить статус заявки':
                text += f'Всего измененных статусов: {len(v)}\n'

        await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], text)

    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'На этапе формирования статистики')
