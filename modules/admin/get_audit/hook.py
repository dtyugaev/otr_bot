# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru


"""
Модуль для сбора статистики
"""

import logging
import os

from aiogram import types

from core import core_db, resources, core_modules


async def check_args(message: types.Message):
    """
    Получаем аргументы команды

    :param message:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
        _help = '/get_audit [id пользователя] [число в днях за которое нужен отчет]\n\nНапример:\n/get_audit [12345678] [5] - выдаст отчет по пользователю 12345678 за последние 5 дней включая текущий'


        args = message.get_args().split()

        if len(args) == 1:
            try:
                int(args[0])
            except Exception:
                await message.answer(_help)
                return 1
        elif len(args) == 2:
            try:
                int(args[0])
                int(args[1])
            except Exception:
                await message.answer(_help)
                return 1
        elif len(args) > 2:
            await message.answer(_help)
            return 1



        if len(args) == 0:
            mode = 'full'
        elif len(args) == 1:
            mode = f'full user {args[0]}'
        elif len(args) == 2:
            mode = f'limit user {args[0]} {args[1]}'
        else:
            await message.answer(_help)
            return 1

        logging.debug(f"Try export audit this mode: {mode}")

        if mode == 'full':
            data = core_db.api.get_audit()
        elif 'full user' in mode:
            data = core_db.api.get_audit(int(args[0]))
        elif 'limit user' in mode:
            data = core_db.api.get_audit(int(args[0]), int(args[1]))
        else:
            await message.answer(f"Не найдено условие для выполнения поиска в бд: {mode}")
            return 1

        if not data:
            await message.answer(f"Данные для условия: {mode} не найдены")
            return 1

        audit_file_path = await core_modules.generate_audit_file(data)
        await resources.data.bot.send_document(resources.data.config['Telegram']['approval_group_id'], types.InputFile(audit_file_path), caption=f"Выгружны данные по условию: {mode}")
        os.remove(audit_file_path)

    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'На этапе формирования аудита')