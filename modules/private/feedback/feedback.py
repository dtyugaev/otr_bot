# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
"""
модуль обратной связи для пользователя
"""
import logging
from random import randint

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_core import states
from core import core_modules, core_db, resources
from . import keyboards


async def cancel(message: types.Message, state: FSMContext):
    """
    Отмена создания обращения

    :param message:
    :param state:
    :return:
    """
    core_db.api.add_audit(message.from_user.id, f'Ввел команду {message.text}')
    await state.finish()
    await message.answer('Операция отменена', reply_markup=keyboards.generate_startup_menu())


async def hook_answer(message: types.Message, state: FSMContext):
    """
    Получили ответ от администратора

    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    await resources.data.bot.forward_message(chat_id=data['id_user'], from_chat_id=message.chat.id, message_id=message.message_id)
    await resources.data.bot.send_message(chat_id=data['id_user'], text=f"Пришел ответ на Ваше обращение: {data['id_issue']}")
    await resources.data.bot.send_message(chat_id=resources.data.config['Telegram']['approval_group_id'], text=f'Ответ на обращение {data["id_issue"]} отправлен')
    await state.finish()


async def answer_message(message: types.CallbackQuery, state: FSMContext):
    """
    Отвечаем на обращение

    :param message:
    :return:
    """
    try:
        id_user = message.data.split(':')[2]
        id_issue = message.data.split(':')[1]
        try:
            await message.message.delete_reply_markup()
        except Exception:
            logging.exception("Error delete reply")
            await state.finish()
            return 1
        core_db.api.add_audit(message.from_user.id, f'Отвечает на фидбек: {id_issue}')
        await message.message.answer(
            f"Ответ на обращение: {id_issue}\nОтветьте пользователю и приложите файл, если необходимо\n\nПодсказка: прикладывайте текст и файлы в одном сообщении. Прикладывать один файл. Если нужно приложить несколько, то используйте zip архив. Размер файла не должен превышать 15мб")
        await state.update_data(id_user=id_user, id_issue=id_issue)
        await states.Feedback.wait_answer.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка в обратной связи')
        await state.finish()


async def hook_message(message: types.Message, state: FSMContext):
    """
    Получили сообщение от пользователя

    :param message:
    :param state:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Ввел данные для фидбека')
        id_issue = str(randint(00000, 99999))
        user_data = core_db.api.get_user_profile(message.from_user.id)
        await resources.data.bot.forward_message(chat_id=resources.data.config['Telegram']['approval_group_id'], from_chat_id=message.from_user.id, message_id=message.message_id)
        await resources.data.bot.send_message(chat_id=resources.data.config['Telegram']['approval_group_id'], text=f"Новое обращение от пользователя:\nID: '%s'\nФИО: {user_data['fio']}\nИД ОБРАЩЕНИЯ: {id_issue}" % message.from_user.id,
                                              reply_markup=keyboards.kb_answer_feedback(id_issue, message.from_user.id))
        await message.answer(f"Ваше обращение '{id_issue}' принято и будет рассмотрено администраторами", reply_markup=keyboards.generate_startup_menu())
        await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка в обратной связи')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def start(message: types.Message, state: FSMContext):
    """
    Пользователь запустил модуль

    :param message:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Ввел команду {message.text}')
        await message.answer(
            "Если у Вас возник вопрос, связанный с работой бота, пожалуйста, опишите проблему и приложите файл при необходимости.\n\nПодсказка: текст и файл должны быть в одном сообщении. Если требуется приложить несколько файлов, то используйте zip архив. Размер не должен превышать 15Мб.\n\nДля прямого обращения к сотрудникам Службы технической поддержки, пожалуйста, позвоните по телефону +7 (495) 223-07-99 (ext. 61555) или напишите на почту: it@otr.ru.",
            reply_markup=keyboards.kb_cancel())

        await states.Feedback.wait_message.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка в обратной связи')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()
