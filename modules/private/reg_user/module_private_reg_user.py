# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
import asyncio
import concurrent.futures
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

import core.core_db.api
from bot_core import states
from core import core_modules, core_db, resources, system
from . import keyboards

max_spam = 10
"""
Модуль, который реагирует на команду /regme и регистрирует пользователя

"""


async def cancel(message: types.Message, state: FSMContext):
    core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
    if core.core_db.api.is_user_registered(message.from_user.id):
        core_db.api.delete_user(message.from_user.id)
    await message.answer("Отмена регистрации. Чтобы начать регистрацию: /regme", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def formatter_email(message, code: int) -> str:
    text = "Для вашего профиля был запрошен проверочный код в рамках прохождения регистрации в боте\n\n" \
           f"Ваш код: {code}\n\n" \
           f"Telegram ID: {message.from_user.id}\nLast name: {message.from_user.last_name}\nFirst name: {message.from_user.first_name}\n" \
           f"Bot: @{resources.data.bot_data['username']}"

    return text


async def recode(message: types.CallbackQuery, state: FSMContext):
    """
    Отправка нового кода по запросу

    :return:
    """
    try:
        try:
            await message.message.delete()
        except Exception:
            return

        state_data = await state.get_data()
        if 'spam' not in state_data.keys():
            state_data['spam'] = 1
        else:
            state_data['spam'] += 1

        if state_data['spam'] > max_spam:
            core_db.api.add_spammer(message.from_user.id)
            await message.message.answer("Вы заблокированы", reply_markup=types.ReplyKeyboardRemove())
            await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], f"Пользователь {message.from_user.id} ({message.from_user.first_name} {message.from_user.last_name}) добавлен в список спаммеров!⚠⚠⚠")
            await state.finish()
            return
        await state.update_data(spam=state_data['spam'])

        new_code = core_db.api.generage_reg_code(message.from_user.id)
        logging.info(f"new code for user: {message.from_user.id} is {new_code}")

        profile_data = core_db.api.get_user_profile(message.from_user.id)
        system.send_email([profile_data['email']], 'Проверочный код для регистрации в боте', formatter_email(message, new_code))

        await message.message.answer("Новый код отправлен на Вашу электронную почту", reply_markup=keyboards.kb_recode())

    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка при регистрации пользователя')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def add_code(message: types.Message, state: FSMContext):
    """
    Пользователь отправил код боту

    :param message:
    :param state:
    :return:
    """
    try:
        if not message.text:
            await message.answer("Некоректные данные. Введите еще раз", reply_markup=keyboards.kb_cancel())
            return

        try:
            enter_code = int(message.text)
        except Exception:
            await message.answer("Некоректные данные. Введите еще раз", reply_markup=keyboards.kb_cancel())
            return

        core_db.api.add_audit(message.from_user.id, f'Введен код {message.text}')

        code_from_db = core_db.api.get_reg_code(message.from_user.id)
        if enter_code != code_from_db:
            state_data = await state.get_data()
            if 'error_code' not in state_data.keys():
                state_data['error_code'] = 1
            else:
                state_data['error_code'] += 1

            if 'spam' not in state_data.keys():
                state_data['spam'] = 1
            else:
                state_data['spam'] += 1

            if state_data['spam'] > max_spam:
                core_db.api.add_spammer(message.from_user.id)
                await message.answer("Вы заблокированы", reply_markup=types.ReplyKeyboardRemove())
                await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'],
                                                      f"Пользователь {message.from_user.id} ({message.from_user.first_name} {message.from_user.last_name}) добавлен в список спаммеров!⚠⚠⚠")
                await state.finish()
                return

            if state_data['error_code'] > 3:
                new_code = core_db.api.get_reg_code(message.from_user.id)
                logging.info(f"new code for user: {message.from_user.id} is {new_code}")
                profile_data = core_db.api.get_user_profile(message.from_user.id)
                system.send_email([profile_data['email']], 'Проверочный код для регистрации в боте', formatter_email(message, new_code))
                await message.answer("Отправлен новый код", reply_markup=keyboards.kb_recode())
                await state.update_data(error_code=1)
                return

            await message.answer("Некорректный код", reply_markup=keyboards.kb_recode())
            await state.update_data(error_code=state_data['error_code'])
            await state.update_data(spam=state_data['spam'])
            return

        core_db.api.approve_user(message.from_user.id)
        profile_info = core_db.api.get_user_profile(message.from_user.id)
        await message.answer(f"Доброго дня, {profile_info['fio']}")
        await message.answer(f"Профиль подтвержден. Вы успешно зарегистрированы.", reply_markup=keyboards.generate_startup_menu())
        await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], f'Зарегистрирован новый пользователь\n\nФИО: {profile_info["fio"]}\nemail: {profile_info["email"]}')
        await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка при регистрации пользователя')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def add_email(message: types.Message, state: FSMContext):
    """
    Пользователь отправил ответ на запрос почты

    :param message:
    :param state:
    :return:
    """
    try:
        email = message.text.lower()
        if not email or not '@' in email:
            await message.answer("Некоректные данные. Введите еще раз", reply_markup=keyboards.kb_cancel())
            return

        core_db.api.add_audit(message.from_user.id, f'Введена почта {email}')
        await message.answer("Проверяю....", reply_markup=keyboards.kb_cancel())
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, resources.data.jira.jira.search_users, email, 0, 999999)

        if not result:
            await message.answer("Некорректный адрес почты или почта не зарегистрирована. Воспользуйтесь командой /regme чтобы повторить попытку авторизации", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            return

        found_user = None
        for i in result.iterable:
            if i.emailAddress.lower() == email:
                found_user = i
                break

        if not found_user:
            await message.answer("Некорректный адрес почты или почта не зарегистрирована. Воспользуйтесь командой /regme чтобы повторить попытку авторизации", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            return

        core_db.api.new_user_profile(message.from_user.id, {'fio': found_user.displayName, 'email': email, 'login': found_user.name})
        new_code = core_db.api.generage_reg_code(message.from_user.id)
        logging.info(f"new code for user: {message.from_user.id} is {new_code}")

        system.send_email([email], 'Проверочный код для регистрации в боте', formatter_email(message, new_code))
        await message.answer("Проверьте почту и введите проверочный код", reply_markup=keyboards.kb_cancel())
        await states.Register_process.wait_code.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка при регистрации пользователя')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def spam(message, state: FSMContext):
    """
    Сообщение для спамера
    :return:
    """
    try:
        if isinstance(message, types.Message):
            await message.delete()
            await message.answer("Подозрение на спам. Вы заблокированы", reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.message.delete()
            await message.message.answer("Подозрение на спам. Вы заблокированы", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка при регистрации пользователя')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def start(message: types.Message, state: FSMContext):
    """
    main
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Попытка зарегистрироваться')

        if core_db.api.is_user_approved(message.from_user.id):
            await message.answer("Вы уже зарегистрированы", reply_markup=keyboards.generate_startup_menu())
            return

        if core_db.api.is_user_registered(message.from_user.id):
            await message.answer("Вам уже отправлен код.", reply_markup=keyboards.kb_recode())
            await states.Register_process.wait_code.set()
            return

        await message.answer("Для создания профиля пользователя введите адрес корпоративной электронной почты.", reply_markup=keyboards.kb_cancel())
        await states.Register_process.wait_email.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка при регистрации пользователя')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()
