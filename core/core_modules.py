# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
"""
Ядро для общих модулей

"""
import datetime
import logging
import os
import zipfile

import xlsxwriter
from aiogram import types, exceptions

from core import constant, resources, core_db


async def isuser_add_bot_to_blacklist(tg_id):
    """
    Проверяем на то, что пользователь добавил бота в черный список

    :param tg_id:
    :return:
    """
    try:
        data = await resources.data.bot.send_chat_action(tg_id, action='typing')
        return False
    except exceptions.BotBlocked:
        return True

async def save_telegram_attach(type_file, tg_id, message):

    """
    Сохраняем аттач из телеги и возвращаем путь до файла


    :param type_file:
    :param tg_id:
    :param message:
    :return:
    """

    path_folder = os.path.join(constant.STORAGE, str(tg_id))
    os.makedirs(path_folder, exist_ok=True)
    if type_file == 'photo':
        while True:
            file_path = os.path.join(path_folder, str(datetime.datetime.now().strftime("%d%m%Y%H%M%S")) + '.jpg')
            if os.path.isfile(file_path):
                continue
            else:
                break
        await message.photo[-1].download(file_path)
        return file_path
    elif type_file == 'document':
        file_name = message.document.file_name
        dcp = await resources.data.bot.download_file_by_id(message.document.file_id, os.path.join(path_folder, file_name))
        return os.path.abspath(dcp.name)

async def generate_archive_logs():
    """
    Подготавливаем архив с логами

    :return:
    """
    log_path = os.path.join(constant.STORAGE, 'log%s.zip' % datetime.datetime.now().strftime("%d%m%Y%H%M%S"))

    __zipf = zipfile.ZipFile(log_path, 'w', zipfile.ZIP_DEFLATED)
    for i in os.listdir(constant.LOGS):
        file_path = os.path.join(constant.LOGS, i)
        __zipf.write(file_path)
    __zipf.close()
    return log_path

async def send_logs(tg_id=None, comment=''):
    """
    Отправляем все логи в админский чат

    :return:
    """
    log_path = await generate_archive_logs()
    if tg_id:
        await resources.data.bot.send_document(resources.data.config['Telegram']['approval_group_id'], types.InputFile(log_path), caption="Ошибка у пользователя {}\n{}".format(tg_id, comment))
    else:
        await resources.data.bot.send_document(resources.data.config['Telegram']['approval_group_id'], types.InputFile(log_path), caption=comment)

    if os.path.isfile(log_path):
        logging.debug("removed %s" % log_path)
        os.remove(log_path)

async def generate_audit_file(data: list):
    """
    Подготавливаем файл с аудитом

    :return:
    """
    file_path = os.path.join(constant.STORAGE, 'audit_file%s.xlsx' % datetime.datetime.now().strftime("%d%m%Y%H%M%S"))

    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()

    for i in data:
        c = 0
        for k, v in i.items():
            worksheet.write(0, c, k)
            c += 1
        break

    row = 1
    for i in data:
        c = 0
        for k, v in i.items():
            worksheet.write(row, c, v)
            c += 1
        row += 1

    workbook.close()
    return file_path

async def generate_users_file():
    """
    Подготавливаем файл с списком пользователей

    :return:
    """
    profiles = core_db.api.get_all_user_profile()
    file_path = os.path.join(constant.STORAGE, 'users_file%s.xlsx' % datetime.datetime.now().strftime("%d%m%Y%H%M%S"))

    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()

    if not profiles:
        raise Exception("Not found profiles")


    for k, v in profiles.items():
        c = 0
        for kk, vv in v.items():
            worksheet.write(0, c, kk)
            c += 1
        break

    row = 1
    for k, v in profiles.items():
        c = 0
        for kk, vv in v.items():
            if kk == 'privilege':
                for kkk, vvv in vv.items():
                    worksheet.write(row, c, 'Да' if vvv == 1 else 'Нет')

            elif isinstance(vv, int):
                if len(str(vv)) == 1:
                    worksheet.write(row, c, 'Да' if vv == 1 else 'Нет')
                else:
                    worksheet.write(row, c, vv)
            else:
                worksheet.write(row, c, vv)

            c += 1

        row += 1

    workbook.close()
    return file_path