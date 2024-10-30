# -*- coding: utf-8 -*-

import logging
import os
import random
import string
import zipfile
from email.mime.text import MIMEText
import smtplib
from os import unlink, path, mkdir
from core import constant, resources, core_db

"""
Модуль ядра
"""

def clear_temp_tables():
    """
    Очищаем темповые таблицы перед стартом

    :return:
    """
    assert core_db.api.recreate_code_table()

def send_email(to: list, subject: str, body: str) -> bool:
    """
    Отправка почты

    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = resources.data.config['jira']['login'] + "@otr.ru"
    msg['To'] = ', '.join(to)

    email = smtplib.SMTP('mail.otr.ru', 587)
    email.starttls()
    email.login(resources.data.config['jira']['login'], resources.data.config['jira']['password'])
    email.sendmail('telegram@otr.ru', to, msg.as_string())
    email.quit()

    return True

def remove_file(file_path):
    """
    Удаляем файл, который под блокировкой

    :param file_path:
    :return:
    """
    if not os.path.isfile(file_path):
        return None
    while True:
        try:
            os.remove(file_path)
            logging.debug("Removed %s" % file_path)
            return True
        except Exception:
            logging.exception("Fail deleted %s" % file_path)
            continue


def create_chunks(l: list, max_in_page: int):
    """
    :param l: список того, что надо разбить на страницы
    :param max_in_page: количество записей на страницу
    :return:
    """
    # split all issues in chunks
    total_collect_split_pages = [l[i:i + max_in_page] for i in
                                 range(0, len(l), max_in_page)]
    data = dict()
    for page, i in enumerate(total_collect_split_pages, start=1):
        data[page] = list()
    for page, i in enumerate(total_collect_split_pages, start=1):
        for ii in i:
            if 'область' in ii:
                data[page].append(ii.replace('область', 'обл.'))
                continue
            elif 'Республика' in ii:
                data[page].append(ii.replace('Республика', 'Респ.'))
                continue

            data[page].append(ii)
    return data


def save_file(filename, data):
    '''
    Сохраняет файл в директорию

    :param filename: Имя файла
    :param data: Содержимое файла
    :return: bool True or False
    '''
    if tempdir_exist(path.split(filename)[0]):
        try:
            temp_file = open(filename, 'wb')
            temp_file.write(data)
            temp_file.close()
            return filename
        except:
            logging.exception(f'Can`t save file : {filename} !')
            return False
    else:
        return False


def delete_file(file_path):
    '''
    Удаляет файл по указанному пути

    :param file_path: Путь к файлу
    :return: True or False
    '''
    if path.isfile(file_path):
        try:
            unlink(file_path)
            return True
        except:
            logging.exception(f'Can`t delete file : {file_path} !')
            return False
    else:
        print('Файла не существует')
        return False


def tempdir_exist(tdir):
    '''
    Проверяет, существует ли директория, если нет, то создает ее

    :param tdir: Путь к каталогу
    :return: True or False
    '''

    if not path.exists(tdir):
        try:
            mkdir(tdir)
            return True
        except:
            logging.exception(f'Can`t create directory : {tdir} !')
            return False
    else:
        return True


def gen_random_name(kol_sym):
    '''
    Генерирует рандомное имя

    :param kol_sym: Длина имени
    :return: str
    '''
    return ''.join(random.choice(string.ascii_letters) for i in range(kol_sym))


def check_exist_zipfile():
    '''
    Проверяет существует ли файл с таким сгенерированным именем

    :return: str (имя файла, которого нет в каталоге)
    '''

    while True:
        name_file = gen_random_name(20)
        if not path.isfile(path.join(constant.STORAGE, f'{name_file}.zip')):
            return name_file
        else:
            logging.error(f'--- Файл {name_file}.zip существует ---')


def zip_file(data):
    '''
    Создает архив с вложениями из задачи JIRA

    :param data: Список объектов Attachment
    :return: str (путь к архиву) или False (если не получилось создать)
    '''
    name_file = path.join(constant.STORAGE, f'{check_exist_zipfile()}.zip')

    if tempdir_exist(constant.TMP_DIR) and tempdir_exist(constant.STORAGE):
        try:
            __zipf = zipfile.ZipFile(name_file, 'w', zipfile.ZIP_DEFLATED)

            for attachment in data:
                if save_file(path.join(constant.TMP_DIR, attachment.filename), attachment.get()):
                    __zipf.write(path.join(constant.TMP_DIR, attachment.filename),
                                 path.basename(path.join(constant.TMP_DIR, attachment.filename)))

                    logging.info(f'Created file {path.join(constant.TMP_DIR, attachment.filename)}.')
                    delete_file(path.join(constant.TMP_DIR, attachment.filename))
            __zipf.close()
            logging.info(f'Created zip file {name_file}.')
            return name_file
        except:
            raise Exception('Не удалось создать архив !')
    else:
        return False