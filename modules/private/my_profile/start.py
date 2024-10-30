# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_core import states
from core import core_modules, core_db, resources
from . import keyboards

"""
Модуль, который реагирует на 'Мой профиль' в чате

"""


async def cancel(message: types.Message, state: FSMContext):
    core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
    await message.answer("Работа с профилем завершена", reply_markup=keyboards.generate_startup_menu())
    await state.finish()

async def del_profile(message: types.CallbackQuery, state: FSMContext):
    """
    Удаляем пользователя

    :param message:
    :return:
    """
    try:
        try:
            await message.message.delete_reply_markup()
        except Exception:
            return

        if 'True' in message.data:
            user_data = core_db.api.get_user_profile(message.from_user.id)
            core_db.api.add_audit(message.from_user.id, f'Подтвердил удаление своего профиля')
            if core_db.api.delete_user(message.from_user.id):
                await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], f"Пользователь {user_data['fio']} ({user_data['tg_id']}) удалил свой профиль из базы данных!")
                await message.message.answer("Ваш профиль успешно удален")
                await message.message.answer(
                    'Добрый день! Вас приветствует бот Службы технической поддержки. Для создания профиля и начала использования бота нажмите /regme. Если вы уже зарегистрированы, то ожидайте одобрения администратора',
                    reply_markup=types.ReplyKeyboardRemove())
            else:
                await message.message.answer("Ошибка удаления пользователя. Обратитесь к администратору")
        else:
            core_db.api.add_audit(message.from_user.id, f'Отменил удаление своего профиля')
            await message.message.answer("Операция отменена", reply_markup=keyboards.generate_startup_menu())

        await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка при работе с "мой профиль"')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def hook_del(message: types.CallbackQuery, state: FSMContext):
    """
    пользователь нажал удаление пользователя

    :param message:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Попытка удалить свой профиль')
        try:
            await message.message.delete_reply_markup()
        except Exception:
            return

        await message.message.answer("Выберите действие", reply_markup=keyboards.kb_cancel())
        await message.message.answer("Уверены, что хотите удалить свой профиль?", reply_markup=keyboards.kb_yes_or_not())
        await states.My_profile.del_profile.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка при работе с "мой профиль"')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def my_profile(message: types.Message):
    """
    Модуль, который посылает ответ в чат, на команду 'Мой профиль'

    :param message:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
        profile_info = core_db.api.get_user_profile(message.from_user.id)

        privilege_text = ''
        _p = {'supervisor': 'Привилегия для просмотра всех заявок'}

        for k, v in profile_info['privilege'].items():
            if v == 1:
                privilege_text += '-' + _p[k] + '\n'

        if privilege_text:
            privilege_text = "\n\nВы владеете следующими привилегиями:\n" + privilege_text
        else:
            privilege_text = '\nВы не имеете особых привилегий'

        await message.answer(f"Информация о профиле {profile_info['tg_id']}", reply_markup=keyboards.kb_cancel())
        await message.answer(f"ID: {profile_info['tg_id']}\n"
                             f"ФИО: {profile_info['fio']}\n"
                             f"Почта: {profile_info['email']}\n"
                             f"{privilege_text}", reply_markup=keyboards.kb_menu())
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка при работе с "мой профиль"')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
