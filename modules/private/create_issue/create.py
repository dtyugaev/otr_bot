# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

"""
Создание заявки по кнопке 'создать заявку'
"""

import asyncio
import concurrent.futures
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import FileIsTooBig, TelegramAPIError

from bot_core import states
from core import core_modules, constant, core_db, resources
from . import keyboards

"""
•Из личных сообщений. Пользователь нажимает на кнопку «Новая заявка». 

Бот предлагает ввести тему заявки «Введите тему заявки:», 
далее «Введите описание заявки и прикрепите вложение (если требуется):». 
После ввода появляется сообщение «Информация принята, ожидайте номер созданной заявки».
После регистрации в JIRA бот направляет пользователю сообщение с номером заявки «Заявка SD-194 зарегистрирована. Отслеживание работ по заявке доступно в ЕТД по ссылке https://balancer.fomstls.ru/#/app/issue/SD-194 и в диалоге чат-бота по номеру заявки.».  


"""


async def cancel(message: types.Message, state: FSMContext):
    """
    Отмена создания заявки

    :param message:
    :param state:
    :return:
    """
    core_db.api.add_audit(message.from_user.id, f'Ввел команду {message.text}')
    await state.finish()
    await message.answer('Операция отменена', reply_markup=keyboards.generate_startup_menu())

async def get_accept(message: types.CallbackQuery, state: FSMContext):
    try:
        try:
            await message.message.delete_reply_markup()
        except Exception:
            return

        if message.data.split(':')[1] == 'no':
            core_db.api.add_audit(message.from_user.id, f'Отменил создание заявки')
            await message.message.answer("Отмена операции", reply_markup=keyboards.generate_startup_menu())
            return

        core_db.api.add_audit(message.from_user.id, f'Подтвердил создание заявки')

        st_data = await state.get_data()
        await message.message.answer("Заявка создается...", reply_markup=keyboards.generate_startup_menu())
        loop = asyncio.get_running_loop()
        if '\n' in st_data['subject']:
            st_data['subject'] = ' '.join(st_data['subject'].split('\n'))


        if st_data['attach']:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                issue_key = await loop.run_in_executor(pool, resources.data.jira.create_issue, "IT", st_data['subject'], st_data['desc'], message.from_user.id, st_data['attach'])
        else:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                issue_key = await loop.run_in_executor(pool, resources.data.jira.create_issue, "IT", st_data['subject'], st_data['desc'], message.from_user.id)

        if not issue_key:
            raise Exception("Not issue_key")
        else:
            await message.message.answer(f"Заявка <a href='{resources.data.config['jira']['url']}/servicedesk/customer/portal/6/{issue_key}'>{issue_key}</a> зарегистрирована. Для отслеживания хода работ используйте кнопку Узнать статус.", reply_markup=keyboards.generate_startup_menu(), parse_mode="HTML")

        core_db.api.save_stats(action=constant.STATS_ACTIONS['create_issue'])
        await state.finish()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка заведения заявки')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()


async def get_desc(message: types.Message, state: FSMContext):
    try:
        type_mes = message.content_type
        attach_name = ''
        attach_path = ''
        desc = message.text
        if type_mes == 'photo':
            core_db.api.add_audit(message.from_user.id, f'Приложил фото')
            try:
                attach_path = await core_modules.save_telegram_attach(type_file='photo', tg_id=message.from_user.id, message=message)
            except FileIsTooBig:
                await message.answer("Слишком большой размер файла. Уменьшите размер и приложите еще раз")
                return 1
            attach_name = 'приложена 1 фотография'
            desc = message.caption

        elif type_mes == 'document':
            core_db.api.add_audit(message.from_user.id, f'Приложил документ')
            try:
                attach_path = await core_modules.save_telegram_attach(type_file='document', tg_id=message.from_user.id, message=message)
            except FileIsTooBig:
                await message.answer("Слишком большой размер файла. Уменьшите размер и приложите еще раз")
                return 1
            attach_name = message.document.file_name
            desc = message.caption


        if desc is None:
            await state.update_data(desc='Описание не указано')
        else:
            core_db.api.add_audit(message.from_user.id, f'Ввел описание заявки {desc}')
            await state.update_data(desc=desc)

        data = await state.get_data()
        await state.update_data(attach=attach_path)

        try:
            if attach_name:
                text = f"Проверьте введеные данных и подтвердите создание заявки\n\nТема: {data['subject']}\nОписание: {data['desc']}\nПриложеный файл: {attach_name}"
            else:
                text = f"Проверьте введеные данных и подтвердите создание заявки\n\nТема: {data['subject']}\nОписание: {data['desc']}"

            if len(text) > 4096:
                text = 'Подтвердите создание заявки'
                
            await message.answer(text, reply_markup=keyboards.kb_accept_create())
            await states.Processing_create_issue.wait_accept.set()
        except KeyError:
            logging.exception("Not fatal error. Skipping this callback")
            return 0
    except TelegramAPIError as TAE:
        logging.exception("Fatal error")
        await state.finish()
        if 'gateway' in str(TAE).lower():
            await core_modules.send_logs(message.from_user.id, 'Ошибка заведения заявки. Проблема с сетью')
            await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка. Проблема связи с Telegram. Повторите попытку')
        else:
            await core_modules.send_logs(message.from_user.id, 'Ошибка заведения заявки')
            await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')


    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка заведения заявки')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()

async def get_subject(message: types.Message, state: FSMContext):
    try:
        if not message.content_type == 'text':
            await message.answer('Введите тему заявки', reply_markup=keyboards.kb_cancel())
            return 1
        if len(message.text) > 255:
            await message.answer('Слишком много символов. Тема может содержать до 255 символов. Введите еще раз', reply_markup=keyboards.kb_cancel())
            return 1

        if not message.text:
            logging.debug(f"Subject for {message.from_user.id}: '{message.text}'")
            await message.answer('Введите тему заявки', reply_markup=keyboards.kb_cancel())
            return 1

        core_db.api.add_audit(message.from_user.id, f'Ввел тему заявки заявки {message.text}')
        await state.update_data(subject=message.text)
        await message.answer('Введите описание заявки и прикрепите вложение (если требуется)\n\nПодсказка: прикладывайте текст и файлы в одном сообщении. Прикладывать один файл. Если нужно приложить несколько, то используйте zip архив', reply_markup=keyboards.kb_cancel())
        await states.Processing_create_issue.wait_desc.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка заведения заявки')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()

async def start(message: types.Message, state: FSMContext):
    try:
        core_db.api.add_audit(message.from_user.id, f'Отправил команду {message.text}')
        await message.answer('Введите тему заявки', reply_markup=keyboards.kb_cancel())
        await states.Processing_create_issue.wait_subject.set()
    except Exception:
        logging.exception("Fatal error")
        await core_modules.send_logs(message.from_user.id, 'Ошибка заведения заявки')
        await resources.data.bot.send_message(message.from_user.id, 'Произошла критическая ошибка')
        await state.finish()
