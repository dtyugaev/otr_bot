# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

import asyncio
import concurrent.futures
import logging
import os

from aiogram import exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_core import states
from core import core_modules, constant, core_db, resources
from modules.private.find_issue import find_issue
from . import keyboards


async def get_attach(message: types.CallbackQuery):
    """
    Получаем все вложения из заявки

    :param message:
    :return:
    """
    core_db.api.add_audit(message.from_user.id, f'Нажал кнопку получить вложения')
    try:
        await message.answer()
    except Exception:
        return

    try:
        issue_id = message.data.split(':')[1]

        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            archive_path = await loop.run_in_executor(pool, resources.data.jira.get_issue_attachments_file, issue_id)

        if not archive_path:
            await message.message.answer("Ошибка получения вложений")
            return
        try:
            await message.message.answer_document(types.InputFile(archive_path), caption=f'Вложения {issue_id}')
        except exceptions.NetworkError as ex:
            if 'File too large for uploading' in str(ex):
                await message.message.answer("Не удалось получить вложения. Слишком большой размер")
            else:
                raise ex

        os.remove(archive_path)
    except Exception:
        logging.exception("Fatal error get attach for %s" % message.from_user.id)
        await message.message.answer("Ошибка получения вложений")
        await core_modules.send_logs(message.from_user.id, 'Ошибка процессинга с заявкой')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')



async def cancel(message: types.Message, state: FSMContext):
    """
    Отмена операции

    :param message:
    :return:
    """
    core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
    await state.finish()
    await message.answer('Операция отменена', reply_markup=keyboards.generate_startup_menu())


async def close(message: types.CallbackQuery):
    """
    подтверждаем решение

    :param message:
    :return:
    """
    try:
        try:
            await message.answer()
        except Exception:
            return

        core_db.api.add_audit(message.from_user.id, f'Нажал кнопку подтвердить решение')
        mes = await resources.data.bot.send_message(message.from_user.id, 'Обрабатываем...', reply_markup=keyboards.generate_startup_menu())


        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            res_sw = await loop.run_in_executor(pool, resources.data.jira.switch_status, 'Закрыть', message.data.split(':')[1], 'Пользователь подтвердил решение заявки')


        if res_sw == 0:
            await message.message.answer(f'Заявка {message.data.split(":")[1]} закрыта', reply_markup=keyboards.generate_startup_menu())
            core_db.api.save_stats(action=constant.STATS_ACTIONS['proc_status'])
        else:
            await message.message.answer('Ошибка закрытие заявки', reply_markup=keyboards.generate_startup_menu())

        await mes.delete()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка процессинга с заявкой')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')

async def reopen(message: types.Message, state: FSMContext):
    """
    переоткрываем

    :param message:
    :param state:
    :return:
    """
    try:
        mes = await message.answer('Обрабатываем...', reply_markup=types.ReplyKeyboardRemove())
        state_d = await state.get_data()
        user_data = core_db.api.get_user_profile(message.from_user.id)
        type_mes = message.content_type
        attach_name = ''
        attach_path = ''
        if type_mes == 'photo':
            core_db.api.add_audit(message.from_user.id, f'Приложено фото')
            attach_path = await core_modules.save_telegram_attach(type_file='photo', tg_id=message.from_user.id, message=message)
            attach_name = 'приложена 1 фотография'
        elif type_mes == 'document':
            core_db.api.add_audit(message.from_user.id, f'Приложен документ')
            attach_path = await core_modules.save_telegram_attach(type_file='document', tg_id=message.from_user.id, message=message)
            attach_name = message.document.file_name

        com = message.caption
        core_db.api.add_audit(message.from_user.id, f'Введены данные {com}')

        if com is None:
            if message.text is None:
                com = f"(Заявитель) [{user_data['fio']}]: Приложен файл"
            else:
                com = f"(Заявитель) [{user_data['fio']}]: " + message.text

        loop = asyncio.get_running_loop()

        with concurrent.futures.ThreadPoolExecutor() as pool:
            # переоткрыть было изменено на 'Переоткрыть_для_робота' в рамках решения проблемы с уведомлениями
            if type_mes in ('photo', 'document'):
                com_res = await loop.run_in_executor(pool, resources.data.jira.switch_status, 'Переоткрыть', state_d['issue_id'], com, attach_path)
            else:
                com_res = await loop.run_in_executor(pool, resources.data.jira.switch_status, 'Переоткрыть', state_d['issue_id'], com)

        if com_res == 0:
            await message.answer('Комментарий добавлен.', reply_markup=keyboards.generate_startup_menu())
            core_db.api.save_stats(action=constant.STATS_ACTIONS['proc_status'])
        else:
            await message.answer('Ошибка добавления комментария', reply_markup=keyboards.generate_startup_menu())

        await mes.delete()
        await find_issue.process_find_issue(message, state, state_d['issue_id'])
        await state.finish()
    except Exception:
        state_info = await state.get_data()
        logging.info(str(state_info))
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка процессинга с заявкой')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def wait_reopen(message: types.CallbackQuery, state: FSMContext):
    """
    ожидаем комментарий для переоткрытия заявки

    :param message:
    :param state:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Нажал кнопку переоткрыть')
        try:
            await message.answer()
        except Exception:
            return


        mes = await resources.data.bot.send_message(message.from_user.id, 'Собираем информацию по заявке...')
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            issue_actual_info = await loop.run_in_executor(pool, resources.data.jira.get_issue_from_id, message.data.split(':')[1])
        await mes.delete()

        if issue_actual_info['Текущий статус'] != 'Подтверждение решения':
            await message.message.answer("Информация уже предоставлена.")
            await state.finish()
            return

        await message.message.answer("Введите, пожалуйста, комментарий и прикрепите вложение (строго в одном сообщении)\n\nПодсказка: прикладывайте текст и файлы в одном сообщении. Прикладывать один файл. Если нужно приложить несколько, то используйте zip архив. Размер файла не должен превышать 15мб", reply_markup=keyboards.kb_cancel())
        await state.update_data(issue_id=message.data.split(':')[1])
        await states.Processing_issue_comment.wait_reopen.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка процессинга с заявкой')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def give_info(message: types.Message, state: FSMContext):
    """
    Получили коммент

    :param message:
    :param state:
    :return:
    """
    try:
        mes = await message.answer('Обрабатываем...', reply_markup=types.ReplyKeyboardRemove())
        user_data = core_db.api.get_user_profile(message.from_user.id)
        state_d = await state.get_data()

        if not state_d:
            logging.error("Empty state_d")
            return 1

        type_mes = message.content_type
        attach_name = ''
        attach_path = ''
        if type_mes == 'photo':
            core_db.api.add_audit(message.from_user.id, f'Приложено фото')
            attach_path = await core_modules.save_telegram_attach(type_file='photo', tg_id=message.from_user.id, message=message)
            attach_name = 'приложена 1 фотография'
        elif type_mes == 'document':
            core_db.api.add_audit(message.from_user.id, f'Приложен файл')
            attach_path = await core_modules.save_telegram_attach(type_file='document', tg_id=message.from_user.id, message=message)
            attach_name = message.document.file_name

        com = message.caption
        core_db.api.add_audit(message.from_user.id, f'Введены данные {com}')


        if com is None:
            if message.text is None:
                com = f"(Заявитель) [{user_data['fio']}]: Приложен файл"
            else:
                com = f"(Заявитель) [{user_data['fio']}]: " + message.text


        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            # ответить изменено на 'Ответ для робота' в рамках решения проблемы с уведомлениями
            if type_mes in ('photo', 'document'):
                res_ws = await loop.run_in_executor(pool, resources.data.jira.switch_status, 'Ответ для робота', state_d['issue_id'], com, attach_path)
            else:
                res_ws = await loop.run_in_executor(pool, resources.data.jira.switch_status, 'Ответ для робота', state_d['issue_id'], com)

        if res_ws == 0:
            await message.answer('Комментарий добавлен.', reply_markup=keyboards.generate_startup_menu())
            core_db.api.save_stats(action=constant.STATS_ACTIONS['proc_status'])
        else:
            await message.answer('Ошибка добавления комментария', reply_markup=keyboards.generate_startup_menu())

        await mes.delete()
        await find_issue.process_find_issue(message, state, state_d['issue_id'])
        await state.finish()
    except Exception:
        state_data = await state.get_data()
        logging.info("STATE: %s" % str(state_data))
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка процессинга с заявкой')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def wait_give_info(message: types.CallbackQuery, state: FSMContext):
    """
    ожидаем предоставление информации

    :param message:
    :param state:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Нажал кнопку предоставить информацию')
        try:
            await message.answer()
        except Exception:
            return

        loop = asyncio.get_running_loop()
        _up = await resources.data.bot.send_message(message.from_user.id, 'Получаем актуальную информацию...')
        with concurrent.futures.ThreadPoolExecutor() as pool:
            issue_actual_info = await loop.run_in_executor(pool, resources.data.jira.get_issue_from_id, message.data.split(':')[1])
        await _up.delete()

        if issue_actual_info['Текущий статус'] != 'Запрос информации':
            await state.finish()
            await message.message.answer("Информация уже предоставлена.")
            return

        await message.message.answer("Введите, пожалуйста, комментарий и прикрепите вложение (строго в одном сообщении)\n\nПодсказка: прикладывайте текст и файлы в одном сообщении. Прикладывать один файл. Если нужно приложить несколько, то используйте zip архив. Размер файла не должен превышать 15мб", reply_markup=keyboards.kb_cancel())
        await state.update_data(issue_id=message.data.split(':')[1])
        await states.Processing_issue_comment.wait_give_info.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка процессинга с заявкой')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()

async def add_comment(message: types.Message, state: FSMContext):
    """
    Получили коммент

    :param message:
    :param state:
    :return:
    """
    try:
        mes = await message.answer('Обрабатываем...', reply_markup=types.ReplyKeyboardRemove())
        com = message.caption
        if com is None:
            com = message.text
            if com is None:
                com = 'Приложен файл'
            core_db.api.add_audit(message.from_user.id, f'Введены данные {com}')

        state_d = await state.get_data()
        if not state_d:
            logging.warning("Empty state_d")
            return 1

        type_mes = message.content_type
        profile_data = core_db.api.get_user_profile(message.from_user.id)
        attach_name = ''
        attach_path = ''
        if type_mes == 'photo':
            core_db.api.add_audit(message.from_user.id, f'Добавлено фото')
            attach_path = await core_modules.save_telegram_attach(type_file='photo', tg_id=message.from_user.id, message=message)
            attach_name = 'приложена 1 фотография'
        elif type_mes == 'document':
            core_db.api.add_audit(message.from_user.id, f'Добавлен документ')
            attach_path = await core_modules.save_telegram_attach(type_file='document', tg_id=message.from_user.id, message=message)
            attach_name = message.document.file_name

        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            if type_mes in ('photo', 'document'):
                com_res = await loop.run_in_executor(pool, resources.data.jira.add_comments, f"(Заявитель) [{profile_data['fio']}]: " + com, state_d['issue_id'], attach_path)
            else:
                com_res = await loop.run_in_executor(pool, resources.data.jira.add_comments, f"(Заявитель) [{profile_data['fio']}]: " + com, state_d['issue_id'])

        if com_res:
            await message.answer('Комментарий добавлен.', reply_markup=keyboards.generate_startup_menu())
            core_db.api.save_stats(action=constant.STATS_ACTIONS['proc_comment'])
        else:
            await message.answer('Ошибка добавления комментария', reply_markup=keyboards.generate_startup_menu())

        await mes.delete()
        await find_issue.process_find_issue(message, state, state_d['issue_id'])
        await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка процессинга с заявкой')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()

async def wait_comment(message: types.CallbackQuery, state: FSMContext):
    """
    Ожидаем коммент

    :param message:
    :param state:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Нажал на кнопку добавить комментарий')
        try:
            await message.answer(cache_time=300)
        except Exception:
            logging.warning("Query is too old and response timeout expired or query id is invalid for: %s" % message.data.split(':')[1])
            pass

        await message.message.answer("Введите, пожалуйста, комментарий и прикрепите вложение (строго в одном сообщении)\n\nПодсказка: прикладывайте текст и файлы в одном сообщении. Прикладывать один файл. Если нужно приложить несколько, то используйте zip архив. Размер файла не должен превышать 15мб", reply_markup=keyboards.kb_cancel())
        await states.Processing_issue_comment.wait_comment.set()
        await state.update_data(issue_id=message.data.split(':')[1])
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка процессинга с заявкой')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()

    """
    Появляется сообщение «Введите, пожалуйста, комментарий и прикрепите вложение.» После обновления заявки в JIRA пользователю выводится «Комментарий добавлен.» Комментарий и вложение добавляется в заявку.
    """


