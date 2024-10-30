# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types

from core import resources

"""
Модуль, который реагирует на команду /help

"""

async def cmd_help(message: types.Message):
    """
    Модуль, который посылает ответ в чат, на команду '/help'

    :param message:
    :return:
    """
    #core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')

    text = ''

    if message.chat.id == resources.data.config['Telegram']['approval_group_id']:
        text += '/list_users <критерий поиска>- поиск пользователя\n' \
            '/install_priv - выдать права пользователю\n' \
            '/remove_priv - снять права с пользователя\n' \
            '/get_users - выгрузить пользователей в файл\n' \
            '/get_logs - получить логи\n' \
            '/get_chat_info - получить информацию о чате\n' \
            '/stat <day, week, month> - получить статистику\n' \
            '/senduser - отправка сообщения в ЛС пользователю\n' \
            '/broadcast <текст> - отправка сообщений в ЛС всем пользователям.\n' \
            '/get_audit [id] [за срок дней] - получит аудит. [id] - пользователь. [за срок дней] - за N число дней\n' \

    text += '/help - справка\n' \
        '/status - информация о работе бота\n'
    await message.reply(text)
