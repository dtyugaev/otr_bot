# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

import asyncio
import concurrent.futures
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from bot_core import states
from core import core_modules, constant, core_db, resources
from . import keyboards

"""
Модуль, который реагирует на команду кнопку 'Найти заявку по номеру'
"""

async def process_find_issue(message, state: FSMContext, issue_id=None):
    """
     Начинаем поиск заявки


    :param message:
    :param state:
    :return:
    """
    tg_id = message.from_user.id
    try:
        isadmin_issue = False
        def com_chunk():
            result = list()

            text = '<i>Комментарии:</i>\n\n'
            for co in issue_data['comment_list']:
                if len(text) > 4096:
                    if text:
                        result.append(text)
                    text = ''
                    continue

                if (len(text) + len(co)) >= 4096:
                    if text:
                        result.append(text)
                    text = ''
                    if len(co) >= 4096:
                        #нарезаем большой коммент на части
                        n = 4096
                        _m = [co[i:i + n] for i in range(0, len(co), n)]
                        for _mm in _m:
                            result.append(_mm)
                    else:
                        result.append(co)
                    continue

                else:
                    text += co + '\n\n'

            if text:
                result.append(text)
            return result

        if isinstance(message, types.CallbackQuery):
            if not issue_id:
                try:
                    await message.answer()
                except Exception:
                    return

            entered_issue = message.data.split(':')[1]

            old_message = message
            message = message.message
        else:
            entered_issue = message.text

        if issue_id:
            # Если вызываем функцию из другого плагина
            entered_issue = issue_id

        core_db.api.add_audit(tg_id, f'Пытается найти заявку {entered_issue}')

        await message.answer('Выполняется поиск...', reply_markup=keyboards.generate_startup_menu())
        logging.info(f"Выполняется поиск заявки: {entered_issue} для пользователя {tg_id}")
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            issue_data = await loop.run_in_executor(pool, resources.data.jira.get_issue_from_id, entered_issue)

        if not issue_data:
            logging.info(f"Не найдена заявка {entered_issue} для пользователя {tg_id}")
            await message.answer('Некорректный номер заявки или у вас отсутствует доступ для получения сведений о ней. Обратитесь в Службу технической поддержки по телефону +7 (495) 223-07-99 (ext. 61555) или по e-mail: it@otr.ru')
            await state.finish()
            return

        logging.info(f"Поиск заявки {entered_issue} для пользователя {tg_id} завершен")
        user_data = core_db.api.get_user_profile(tg_id)
        if not user_data:
            raise Exception(f"Not found user this id: {tg_id}")


        if issue_data['email'].strip() != user_data['email'].strip():
            if not user_data['privilege']['supervisor'] == 1:
                await message.answer('Некорректный номер заявки или у вас отсутствует доступ для получения сведений о ней. Обратитесь в Службу технической поддержки по телефону +7 (495) 223-07-99 (ext. 61555) или по e-mail: it@otr.ru')
                logging.warning(f"Пользователь {user_data['fio']} ({tg_id}) попытался получить доступ к заявке {entered_issue}. Доступ ограничен. email автора: {issue_data['email']}, email пользователя {user_data['email']}")
                await state.finish()
                return
            logging.info(f"Пользователь получил доступ к заявке {entered_issue} так как у него есть привелегия supervsor")
        else:
            isadmin_issue=True

        mes_base = f"<i>Номер заявки:</i> <a href='{resources.data.config['jira']['url']}/servicedesk/customer/portal/6/{issue_data['Номер заявки']}'>{issue_data['Номер заявки']}</a>" \
            f"\n<i>Тема заявки:</i> <strong>{issue_data['Тема заявки']}</strong>" \
            f"\n<i>Дата создания:</i> <strong>{issue_data['Дата создания']}</strong>" \
            f"\n<i>Дата обновления:</i> <strong>{issue_data['Дата обновления']}</strong>" \
            f"\n<i>Текущий статус:</i> <strong>{issue_data['Текущий статус']}</strong>" \
            f"\n<i>Количество вложений:</i> <strong>{issue_data['Количество вложений']}</strong>"

        #mes_additionally = f"\n<i>Описание заявки:</i> <strong>{issue_data['Описание заявки']}</strong>\n" \

        # mes_additionally_not_html = f"\nОписание заявки: {issue_data['Описание заявки']}\n" \
        #                    f"\nКоличество вложений: {issue_data['Количество вложений']}"

        # isbig=False
        # mes_test = mes_base + mes_additionally
        # mes = mes_test
        # if len(mes_test) > 4096:
        #     logging.info(f"Большой размер описания заявки {entered_issue}")
        #     isbig=True

        mes_com = f"<i>Последний комментарий:</i>\n\n{issue_data['Комментарии']}"

        # if isbig:
        #     await message.answer(mes_base, reply_markup=keyboards.generate_startup_menu(), parse_mode=types.ParseMode.HTML, disable_web_page_preview=True)
        #     for x in range(0, len(mes_additionally_not_html), 4096):
        #         await message.answer(mes_additionally_not_html[x:x + 4096], reply_markup=keyboards.generate_startup_menu())
        # else:
        #     await message.answer(mes, reply_markup=keyboards.generate_startup_menu(), parse_mode=types.ParseMode.HTML, disable_web_page_preview=True)
        #
        await message.answer(mes_base, reply_markup=keyboards.generate_startup_menu(), parse_mode=types.ParseMode.HTML, disable_web_page_preview=True)

        if len(mes_com) > 4096:
            comments = com_chunk()
            for num, i in enumerate(comments, start=1):
                if num == len(comments):
                    await message.answer(i, reply_markup=keyboards.kb_processing_issue(issue_data, isadmin_issue), parse_mode=types.ParseMode.HTML, disable_web_page_preview=True)
                else:
                    await message.answer(i, reply_markup=keyboards.generate_startup_menu(), parse_mode=types.ParseMode.HTML, disable_web_page_preview=True)
        else:
            await message.answer(mes_com, reply_markup=keyboards.kb_processing_issue(issue_data, isadmin_issue), parse_mode=types.ParseMode.HTML, disable_web_page_preview=True)


        core_db.api.save_stats(action=constant.STATS_ACTIONS['open_issue'])

        if not issue_id:
            await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(tg_id, 'Ошибка поиска заявки')
        await resources.data.bot.send_message(tg_id, 'Произошла критическая ошибка')
        await state.finish()

async def cancel(message: types.Message, state: FSMContext):
    """
    Отмена операции

    :param message:
    :return:
    """
    core_db.api.add_audit(message.from_user.id, f'Ввел команду {message.text}')
    await state.finish()
    await message.answer('Операция отменена', reply_markup=keyboards.generate_startup_menu())

async def find(message: types.CallbackQuery, state: FSMContext):
    """
     Инициализация поиска заявки
    :param message:
    :return:
    """
    try:
        core_db.api.add_audit(message.from_user.id, f'Нажал кнопку поиска заявки')

        try:
            await message.message.delete()
        except Exception:
            return

        await message.message.answer('Введите номер заявки в формате: IT-123', reply_markup=keyboards.kb_cancel())
        await states.Find_issue.enter_issue.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка поиска заявки')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()
