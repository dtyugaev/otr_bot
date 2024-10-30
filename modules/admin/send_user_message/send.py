# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

import logging

from aiogram import types, exceptions
from aiogram.dispatcher import FSMContext

from bot_core import states
from core import core_modules, core_db, resources
from . import keyboards


async def accept_send(message: types.CallbackQuery, state: FSMContext):
    try:
        try:
            await message.answer()
        except Exception:
            return


        if message.data.split(":")[1] == 'no':
            core_db.api.add_audit(message.from_user.id, f'Отменил отправку сообщения пользователю')
            await message.answer("Отмена")
            await message.message.delete()
        else:
            core_db.api.add_audit(message.from_user.id, f'Подтвердил отправку сообщения пользователю')
            d = await state.get_data()
            await message.message.delete_reply_markup()
            try:
                await resources.data.bot.send_message(d['id'], d['text'])
            except exceptions.ChatNotFound:
                await message.message.answer(f"Не удалось отправить сообщение для пользователя {d['id']}. Пользователей удалил чат с ботом")
        await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'На этапе отправки сообщения пользователю из админского чата')
        await state.finish()


async def send(message: types.Message, state: FSMContext):
    """
    Отправляем сообщение пользователю

    :param message:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
        try:
            data = {'to': message.text.split()[1], 'text': ' '.join(message.text.split()[2:])}
        except Exception:
            await message.answer("Неверно запущена команда. Используйте /senduser <id> <text>")
            return

        if not data['text']:
            logging.error("Empty text for send message to user %s" % data['to'])
            await message.answer("Нельзя отправить пустое сообщение")
            return 1
        await message.answer("Отправляю пользователю '%s' сообщение: '%s'?" % (data['to'], data['text']), reply_markup=keyboards.kb_accept_send())
        await states.Send_admin_message.wait_send.set()
        await state.update_data(id=data['to'], text=data['text'])
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'На этапе отправки сообщения пользователю из админского чата')
        await state.finish()


