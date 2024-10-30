# -*- coding: utf-8 -*-

import datetime
import logging
import os
import sqlite3
import typing
import time
from random import randint
from contextlib import contextmanager
from core import constant, resources, system


class GetSession:
    def dict_factory(self, cursor, row):
        """
        Возвращает инфу из бд в виде словаря

        :param cursor:
        :param row:
        :return:
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def get_session(self) -> sqlite3.Connection:
        if not os.path.isfile(constant.DATABASE_FILE):
            raise Exception(f"Not found database file: {constant.DATABASE_FILE}. Start script update/pre_install.py for created it")
        db = sqlite3.connect(constant.DATABASE_FILE)  # База данных
        db.row_factory = self.dict_factory
        logging.info(f"Соединение с бд установлено: {constant.DATABASE_FILE}")
        return db


"""
Решение с постоянным запросом инстанса бд связано с тем, что создаются блокировки из-за пользованием одного и того же инстанса разными модулями
"""

@contextmanager
def db_connect() -> sqlite3.Cursor:
    db = resources.data.DB
    cur = db.cursor()
    yield cur
    db.commit()
    cur.close()

def is_user_approved(tg_id: int) -> bool:
    """
    Проверка что профиль пользователя подтвержден

    """
    logging.info(f'Проверка подтверждения регистрация профиля для {tg_id}')

    with db_connect() as cur:
        cur.execute("select approved from users where tg_id=?", (tg_id,))
        res = cur.fetchone()

    if not res:
        logging.warning(f"Не найден пользователь в бд: {tg_id} при при проверке подтверждения аккаунта")
        return False

    logging.info(f"Состояние подтверждения профиля для {tg_id}: {res['approved'] == 1}")
    return res['approved'] == 1


def is_user_supervisor(tg_id: int) -> bool:
    """
    Проверка что профиль пользователя имеет возможность просматривать все заявки

    """
    logging.info(f"Проверка привелегии supervisor для пользователя {tg_id}")

    with db_connect() as cur:
        cur.execute("select supervisor from privilege where tg_id=?", (tg_id,))
        res = cur.fetchone()
        if not res:
            logging.warning(f"Пользователь {tg_id} не найден в таблице privilege")
            cur.execute("INSERT INTO privilege(tg_id, supervisor) VALUES (?, 0)", (tg_id,))

    logging.info(f"Состояние привелегии supervisor для пользователя {tg_id}: {res['supervisor'] == 1}")
    if not res:
        return False
    return res['supervisor'] == 1

def save_error(error: str):
    """
    Сохраняем ошибку в бд
    """
    logging.info(f"Записываем ошибку: {error}")
    with db_connect() as cur:
        cur.execute("insert into errors(time_error, error)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), error))
        res = cur.rowcount
        if res == 0:
            raise Exception(f"Ошибка записи ошибки: {error}")

def add_audit(tg_id: int, action: str):
    """
    Запись аудита

    """
    logging.info(f"Записываем аудит для {tg_id}. Действие: {action}")
    with db_connect() as cur:
        cur.execute("SELECT fio FROM users WHERE tg_id=?", (tg_id,))
        fio = cur.fetchone()
        if not fio:
            logging.warning(f"Не найдено ФИО для ID: {tg_id}")
            fio = 'Unknown'
        else:
            fio = fio['fio']

        cur.execute("INSERT INTO audit(tg_id, fio, action, date) VALUES (?, ?, ?, ?)", (tg_id, fio, action, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        res = cur.rowcount
        if res == 0:
            save_error(f"Ошибка записи аудита для {tg_id}, действия: {action}")
            return
        logging.info(f"Записан аудит {action} для {tg_id}")


def get_audit(tg_id: int = None, time: int = None) -> typing.List:
    """
    Получаем аудит пользователя

    :param time

    : Не обязательно. Период в днях начиная с сегодняйшней даты
    :param id: ID пользвателя телеграм
    :return:
    """
    logging.info(f"Получаем аудит для {tg_id}")
    try:
        db = GetSession().get_session()
        all_data = "SELECT * FROM audit order by date DESC"  # день
        all_user = f"SELECT * FROM audit WHERE tg_id={id} order by date DESC"
        user_this_time = f"SELECT * FROM audit WHERE date between strftime('%Y-%m-%d','now', '-{time} days', 'localtime') and strftime('%Y-%m-%d 23:59:59','now', 'localtime') and tg_id={id} order by date DESC"  # неделя
        cur = db.cursor()

        if id is None:
            sql = all_data
        elif time is None:
            sql = all_user
        else:
            sql = user_this_time
        logging.debug(f"try sql: {sql} for date: ({id}, {time})")
        cur.execute(sql)
        data = cur.fetchall()
        db.close()
        if not data:
            return []

        return data

    except Exception:
        logging.exception(f'Не удалось получить аудит для из бд ({id}, {time})')
        raise Exception("Error get audit")


def approve_user(tg_id: int) -> bool:
    """
    Одобрить профиль пользователя
    Возвращает True при удачном обновлении

    :param tg_id: ID пользователя в Телеграмм
    :return: True или False
    """
    db = GetSession().get_session()
    cur = db.cursor()

    cur.execute("UPDATE users SET approved=1 WHERE tg_id=?", (tg_id,))
    db.commit()
    rows=cur.rowcount
    db.close()
    if not rows > 0:
        raise Exception(f"Error approve user {tg_id}")
    return True



def delete_user(tg_id: int) -> bool:
    """
    Удалить профиль пользователя
    Возвращает True при удачном удалении

    :param tg_id: ID пользователя в Телеграмм
    :return: True или False
    """
    db = GetSession().get_session()
    cur = db.cursor()
    cur.execute("DELETE FROM users WHERE tg_id=?", (tg_id,))
    db.commit()
    logging.warning(f'Удалены данные из БД')
    if not cur.rowcount > 0:
        db.close()
        logging.info(f"DELETE FROM users WHERE tg_id={tg_id}")
        raise Exception("Fatal error delete profile from db")

    cur.execute("DELETE FROM privilege WHERE tg_id=?", (tg_id,))
    if not cur.rowcount > 0:
        db.close()
        logging.info(f"DELETE FROM privilege WHERE tg_id={tg_id}")
        raise Exception("Fatal error delete privileges from db")
    db.commit()
    db.close()
    logging.warning(f'Удалены данные из БД для пользователя {tg_id}')
    return True


def check_user_in_privilege(tg_id: int) -> bool:
    """
    Проверяем и добавляем пользователя в таблицу privilege
    :param tg_id:
    :return:
    """


    db = GetSession().get_session()
    cur = db.cursor()
    cur.execute("select * from privilege where tg_id=?", (tg_id,))
    res = cur.fetchall()
    if not res:
        logging.info(f"Not found privileges row for {tg_id}. Create...")
        cur.execute("INSERT INTO privilege(tg_id, supervisor) VALUES (?, 0)", (tg_id,))
        db.commit()

        if not cur.rowcount > 0:
            db.close()
            raise Exception(f"Error create privilege row for {tg_id}")

    db.close()
    return True


def update_privilege(tg_id: int, what, new_value: int) -> bool:
    """
    Обновить поле в привилегиях пользователя

    :param tg_id: ID пользователя в Телеграмм
    :param what: поле
    :param new_value: Новое значение
    :return: True или False
    """
    db = GetSession().get_session()
    fileds = get_list_privileges()
    if what not in fileds:
        db.close()
        raise ValueError("Invalid filed name. Expected one of: %s" % fileds)
    try:
        if not check_user_in_privilege(tg_id):
            db.close()
            raise Exception("Error check user in privilege")

        cur = db.cursor()
        cur.execute(f"UPDATE privilege SET {what}={new_value} WHERE tg_id=?", (tg_id,))
        db.commit()
        rows = cur.rowcount
        db.close()
        return rows > 0
    except Exception:
        db.close()
        logging.exception(f'Не удалось обновить информацию о пользователе в БД')
        return False


def update_userinfo(tg_id, what, new_value) -> bool:
    """
    Обновить поле в профиле пользователя
    what = fio/org/etd_login/email/phone/region/org_inn

    :param tg_id: ID пользователя в Телеграмм
    :param what: поле
    :param new_value: Новое значение
    :return: True или False
    """
    fileds = ['fio', 'org', 'etd_login', 'email', 'phone', 'region', 'org_inn']
    if what not in fileds:
        raise ValueError("Invalid filed name. Expected one of: %s" % fileds)
    db = GetSession().get_session()
    try:
        cur = db.cursor()
        cur.execute(f"UPDATE users SET {what}='{new_value}' WHERE tg_id=?", (tg_id,))
        db.commit()
        rows = cur.rowcount
        db.close()
        return rows > 0
    except Exception:
        db.close()
        logging.exception(f'Не удалось обновить информацию о пользователе в БД !')
        return False


def get_user_profile(tg_id: int) -> typing.Dict:
    """
    Получить профиль пользователя

    :param tg_id: ID пользователя в телеграмм
    :return : Словарь характеристик пользователя
    """
    db = GetSession().get_session()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id=? LIMIT 1", (tg_id,))
    user_data = cur.fetchone()
    if not user_data:
        db.close()
        logging.error(f"Не найден пользователь в бд {tg_id}")
        return {}

    cur.execute(f"SELECT * FROM privilege where tg_id=?", (tg_id,))
    privilege = cur.fetchall()

    if not privilege:
        db.close()
        raise Exception(f"Not found user: {tg_id} in privileges table")

    for i in privilege:
        for k, v in i.items():
            if k == 'tg_id':
                continue
            user_data.update({'privilege': {k: v}})
    db.close()
    return user_data


def get_list_privileges():
    """
    Получить список доступных привилегий (наименование колонок в таблице privileges)

    :return:
    """
    db = GetSession().get_session()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM privilege")
    names = list(map(lambda x: x[0], cursor.description))[1:]
    db.close()
    return names


def get_user_profile_from_attr(attr, value) -> typing.List:
    """
    Получить список пользователей по его атрибуту

    :param attr:
    :return:
    """
    try:
        db = GetSession().get_session()
        data = dict()
        cursor = db.cursor()
        cursor.execute("select * from users")
        names = list(map(lambda x: x[0], cursor.description))[1:]
        if attr not in names:
            db.close()
            raise Exception("Not found attributes in table users")

        cursor.execute(f"SELECT * FROM users where {attr}=?", (value,))
        res = cursor.fetchall()
        if not res:
            db.close()
            return []
        db.close()
        return res
    except Exception as ex:
        db.close()
        logging.exception("Fatal error get user profile")
        raise ex


def get_all_user_profile() -> typing.Dict:
    """
    Получить все профиля пользователей

    """
    db = GetSession().get_session()
    cur = db.cursor()
    cur.execute(f"SELECT * FROM users")
    res = cur.fetchall()
    data = dict()
    if not res:
        db.close()
        raise Exception("Error get all data from users table")

    for i in res:
        cur.execute("SELECT * FROM privilege where tg_id=?", (i['tg_id'],))
        privilege = cur.fetchall()
        if not privilege:
            check_user_in_privilege(i['tg_id'])

            cur.execute("SELECT * FROM privilege where tg_id=?", (i['tg_id'],))
            privilege = cur.fetchall()
            if not privilege:
                db.close()
                raise Exception(f"Not found user: {i['tg_id']} in privileges table")

        for p in privilege:
            for k, v in p.items():
                if k == 'tg_id':
                    continue
                i.update({'privilege': {k: v}})

        data[i['tg_id']] = i
    db.close()
    return data



def is_user_spammer(tg_id: int) -> bool:
    """
    Проверка пользователя на то что он спаммер

    :param tg_id:
    :return:
    """
    db = GetSession().get_session()
    cur = db.cursor()
    cur.execute("SELECT * from spammers where tg_id=?", (tg_id,))
    res = cur.fetchone()
    db.close()
    if res:
        return True
    else:
        return False

def add_try_to_spammers(tg_id: int) -> int:
    """
    Добавляем количество попыток спама пользователю
    :param self: 
    :param tg_id: 
    :return: Общее количество попыток
    """
    db = GetSession().get_session()
    cur = db.cursor()

    res = cur.execute("select try from spammers where tg_id=?", (tg_id,))
    current_value = res.fetchone()

    if not current_value:
        logging.warning(f"Not found values trys for spammer: {tg_id}")
        add_spammer(tg_id)
        current_value = 0
    else:
        current_value['try'] += 1
        current_value = current_value['try']
    cur.execute("update spammers set try=? where tg_id=?", (current_value, tg_id,))
    rows = cur.rowcount
    if rows == 0:
        db.close()
        raise Exception(f"Error add try for spammer: {tg_id}")
    db.commit()
    logging.warning(f"Update try ({current_value}) for spammer {tg_id}")
    db.close()
    return current_value

def add_spammer(tg_id: int) -> bool:
    """
    Добавление спамера

    :param tg_id:
    :return:
    """
    db = GetSession().get_session()
    cur = db.cursor()

    cur.execute("insert into spammers(tg_id) values (?)", (tg_id,))
    db.commit()
    rows = cur.rowcount
    if rows == 0:
        db.close()
        raise Exception(f"Error add spammer: {tg_id}")
    db.close()
    return True

def recreate_code_table() -> bool:
    """
    Пересозадем таблицу с кодами

    """
    db = GetSession().get_session()
    cur = db.cursor()
    create_table = """
        create table code
            (
                tg_id int,
                code int
            );
    """
    create_index = """
    create unique index code_tg_id_uindex
                on code (tg_id);
    """
    try:
        cur.execute("drop table code")
        db.commit()
        logging.info("Удалена таблица code")
    except Exception:
        pass


    cur.execute(create_table)
    cur.execute(create_index)
    res = cur.rowcount
    db.commit()
    if res == 0:
        db.close()
        raise Exception("Error recreate code table")
    logging.info("Создана таблица code")
    db.close()
    return True

def get_reg_code(tg_id: int) -> int:
    """
    Получаем уникальный код регистрации для пользователя

    :param tg_id:
    :return:
    """
    db = GetSession().get_session()
    cur = db.cursor()

    cur.execute("Select * from code where tg_id=?", (tg_id,))
    user = cur.fetchone()
    if not user:
        db.close()
        raise Exception(f"Now found user {tg_id} in code table")

    if not user['code']:
        db.close()
        raise Exception(f"Now found code for {tg_id}")
    db.close()
    return user['code']

def generage_reg_code(tg_id: int) -> int:
    """
    Сохраняем уникальный код в бд для юзера, для проверки

    :param tg_id:
    :return:
    """
    db = GetSession().get_session()
    cur = db.cursor()
    new_code = randint(1111, 9999)

    cur.execute("Select * from code where tg_id=?", (tg_id,))
    user = cur.fetchone()
    if not user:
        cur.execute("insert into code(tg_id, code) values(?, ?)", (tg_id, 1))
        db.commit()


    cur.execute("update code set code=? where tg_id=?", (new_code, tg_id,))
    logging.info(f"Generate new code for user {tg_id}: {new_code}")
    db.commit()
    db.close()
    return new_code


def is_user_registered(tg_id: int) -> bool:
    """
    проверка что профиль пользователя зарегистрирован
    проверка на подтверждение администратором не выполняется

    :param tg_id: ID пользователя в Телеграмм
    :return: True или False
    """
    try:
        db = GetSession().get_session()
        cur = db.cursor()
        cur.execute("SELECT count(tg_id) as res FROM users WHERE tg_id=? LIMIT 1", (tg_id,))
        res = cur.fetchone()
        if not res:
            logging.info(f"SELECT count(tg_id) as res FROM users WHERE tg_id={tg_id} LIMIT 1")
            raise Exception("Error get check user registered")

        if res['res'] == 1:
            return True
        else:
            return False
    except Exception:
        logging.exception(f'Не удалось получить данные из БД')
        return False

def new_user_profile(tg_id: int, profile_info: dict) -> bool:
    """
    Создать профиль пользователя в БД

    :param tg_id:
    :param profile_info:
    :return:
    """
    db = GetSession().get_session()
    cur = db.cursor()

    if not check_user_in_privilege(tg_id):
        raise Exception("Error add user to privilege table")
    try:
        cur.execute("INSERT INTO users(tg_id, fio, email, approved, login) VALUES (?, ?, ?, ?, ?)", (tg_id, profile_info['fio'], profile_info['email'], 0, profile_info['login']))
        db.commit()
        logging.info(f"Registered user: {str(profile_info)}")
        rows = cur.rowcount
        db.close()
        return rows > 0
    except Exception:
        db.close()
        logging.exception('Не удалось добавить пользователя в БД !')
        raise Exception("error add user: %s to database" % tg_id)


def save_stats(action: str) -> bool:
    """
    Сохранить статистику

    :param action:
    :return:
    """
    db = GetSession().get_session()
    cur = db.cursor()
    try:
        cur.execute("INSERT INTO stats(date, action) VALUES (?, ?)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), action))
        db.commit()
        if not cur.rowcount > 0:
            db.close()
            raise Exception("Not added new action: %s" % action)
        db.close()
        return True
    except Exception:
        db.close()
        logging.exception(f'Не удалось добавить статистику в БД')
        return False


def get_stats(def_time) -> typing.List:
    """
    Получаем статистику

    :param def_time: day, week, month
    :return:
    """
    db = GetSession().get_session()
    logging.debug("Get stat for: %s" % def_time)
    today_d = "SELECT * FROM stats WHERE date between strftime('%Y-%m-%d','now', 'localtime') and strftime('%Y-%m-%d 23:59:59','now', 'localtime')"  # день
    today_w = "SELECT * FROM stats WHERE date between strftime('%Y-%m-%d','now', '-7 days', 'localtime') and strftime('%Y-%m-%d 23:59:59','now', 'localtime')"  # неделя
    today_m = "SELECT * FROM stats WHERE date between strftime('%Y-%m-%d','now', '-30 days', 'localtime') and strftime('%Y-%m-%d 23:59:59','now', 'localtime')"  # месяц
    today_a = "SELECT * FROM stats"  # всего
    if def_time == 'day':
        sql = today_d
    elif def_time == 'week':
        sql = today_w
    elif def_time == 'month':
        sql = today_m
    elif def_time == 'all':
        sql = today_a
    else:
        db.close()
        raise Exception("Unkknown time for statistic")

    cur = db.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    db.close()
    return res
