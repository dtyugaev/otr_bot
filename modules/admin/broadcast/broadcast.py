# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

"""
Модуль рассылки сообщений

"""
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_core import states
from core import core_modules, core_db, resources
from . import keyboards


async def send_mes(text, users=None):
    """
    Отправка сообщений пользователям

    """
    error = list()
    profiles = core_db.api.get_all_user_profile()


    if not profiles:
        raise Exception("Not found user profiles")

    for k, v in profiles.items():
        try:
            await resources.data.bot.send_message(k, text)
        except Exception:
            logging.exception("Error send broadcast to %s" % k)
            error.append(k)

    await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], 'Сообщение отправлено %s пользователям' % len(profiles.keys()))
    if error:
        text_e = 'Следующие пользователи не получили сообщение: '
        for i in error:
            text_e += str(i) + ', '
        await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], text_e)


async def accept(callback: types.CallbackQuery, state: FSMContext):
    """
    Подтверждение отправки

    :param callback:
    :param state:
    :return:
    """
    try:

        try:
            await callback.message.delete_reply_markup()
        except Exception:
            return

        if callback.data.split(":")[1] == 'no':
            core_db.api.add_audit(callback.from_user.id, f'Отменил отправку рассылки')
            await callback.answer("Отмена")
            await callback.message.delete()
            await state.finish()
        else:
            core_db.api.add_audit(callback.from_user.id, f'Подтвердил отправку рассылки')
            d = await state.get_data()
            await send_mes(d['text'])
            await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(callback.from_user.id, 'На этапе отправки рассылки')
        await state.finish()


async def get_mes(message: types.Message, state: FSMContext):
    """
    Регистрируем сообщение от админа

    :param message:
    :return:
    """
    help_mes = '/broadcast текст\n\n' \
               'Например: /broadcast всем привет\n\n' \
               'Отправит сообщение всем пользователям бота'

    try:

        text = message.get_args()

        if not text:
            await message.answer(f"Неверно использована команда\n\n{help_mes}")
            return

        core_db.api.add_audit(message.from_user.id, f'Команда {message.text}')
        await message.answer("Всем пользователям, зарегистрированным у чат-бота будет отправлено соообщение:\n\n%s" % text, reply_markup=keyboards.kb_accept_send())
        await state.update_data(text=text)
        await states.Broadcast.wait_accept.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'На этапе отправки рассылки')
        await state.finish()
