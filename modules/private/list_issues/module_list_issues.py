# -*- coding: utf-8 -*-


import asyncio
import concurrent.futures
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from core import core_modules, resources, core_db
from modules.private.find_issue import find_issue
from . import keyboards


async def get_list_issues(fio: str, login: str, inn: str = None):
    """
    Возвращает спсок задач для указанного пользователя

    :param fio: ФИО пользователя
    :param inn: ИНН организации
    :param login: Логин пользователя
    :return: Словарь списков задач

    {'issue_key': 'SD-1', 'summary': 'Тема', 'status': 'В работе'}
    """

    _MOD_LOG = '[get_list_issues]'
    logging.info(_MOD_LOG + ' User fio = ' + str(fio))

    ji = resources.data.jira
    loop = asyncio.get_running_loop()
    if fio and inn:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            total_collect_split_pages = await loop.run_in_executor(pool, ji.get_all_user_issues, fio, login, inn)
        #total_collect_split_pages = await ji.get_all_user_issues(fio, inn)
    else:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            total_collect_split_pages = await loop.run_in_executor(pool, ji.get_all_user_issues, fio, login)

        #total_collect_split_pages = await ji.get_all_user_issues(fio)
    if total_collect_split_pages == 255:
        raise Exception("Error collect issues")


    if total_collect_split_pages:
        try:
            data = dict()
            for page, i in enumerate(total_collect_split_pages, start=1):
                data[page] = list()

            for page, i in enumerate(total_collect_split_pages, start=1):
                for ii in i:
                    data[page].append({'issue_key': ii.key, 'summary': ii.fields.summary, 'status': ii.fields.status.name})

            total_pages = len(data)

            if not data:
                logging.exception("Fatal error parse list issues")
                return False

            logging.info(data)
            return {'tp': total_pages, 'data': data}
        except Exception:
            logging.exception("%s Fatal error get list issues" % _MOD_LOG)
            logging.info("user_data: %s" % str(fio))
            return False
    else:
        return False


async def answer_empty_btn(query: types.CallbackQuery):
    logging.info('An empty button was pressed.')
    await query.answer()



async def get_all_issues(message: types.CallbackQuery, state: FSMContext):
    """
    Выводит список задач в виде кнопок

    :param message:
    :return:
    """
    try:
        try:
            await message.answer()
        except Exception:
            return
        message_data = message.data.split(':')
        if len(message_data) == 4:
            return

        elif len(message_data) == 3:
            issue_id = message_data[1]
            await find_issue.process_find_issue(message, state, issue_id)
            return

        core_db.api.add_audit(message.from_user.id, f'Нажал кнопку список заявок')
        _m = await message.message.answer("Подготавливаю список Ваших заявок...")
        user_data = core_db.api.get_user_profile(message.from_user.id)
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            all_issues = await loop.run_in_executor(pool, resources.data.jira.get_all_user_issues, user_data['email'])
        await _m.delete()

        """
        
        'issue:{i.key}:{page_number}'
        'issue:page:null:{page_number}'
        'issue:page:null:prev:{page_number}'
        """
        if not all_issues:
            await message.message.answer("Заявки не найдены", reply_markup=keyboards.generate_startup_menu())
            return

        if len(message_data) == 1:
            await message.message.answer("Ваши заявки", reply_markup=keyboards.kb_generate_issue_button(all_issues, 0))

        elif len(message_data) == 5:
            mode = message_data[3]
            if mode == 'prev':
                await message.message.edit_reply_markup(reply_markup=keyboards.kb_generate_issue_button(all_issues, int(message_data[4]) - 1))
            else:
                await message.message.edit_reply_markup(reply_markup=keyboards.kb_generate_issue_button(all_issues, int(message_data[4]) + 1))

    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка в выводе списка заявок пользователя')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')

