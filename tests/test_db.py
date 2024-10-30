# -*- coding: utf-8 -*-

"""

Тесты для статистики

"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from core import core_db, constant

rotate = logging.handlers.RotatingFileHandler(os.path.join(constant.LOGS, 'log_test_db.txt'), maxBytes=10000000,
                              backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG, handlers=[rotate, consoleHandler])

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.info("\nStart test")

tg_id = 1234567890
tg_id_dup = 12345678901
tg_id_not_dup = 123456789012
fio = 'Питоновский тестовый тест'
fio_not_dup = 'тестовый тест тест'
email = 'python@otr.ru'
profile_info = {'fio': fio,
                'email': email}


def test_create_new_user():
    """
    Создание нового профиля
    :return:
    """
    assert core_db.api.new_user_profile(tg_id, profile_info=profile_info)
    assert core_db.api.new_user_profile(tg_id_dup, profile_info=profile_info)
    profile_info_not_dup = profile_info
    profile_info_not_dup['tg_id'] = tg_id_not_dup
    profile_info_not_dup['fio'] = fio_not_dup
    assert core_db.api.new_user_profile(tg_id_not_dup, profile_info=profile_info_not_dup)

def test_add_try_spammer():
    """
    Добавление попыток спама для спаммера
    :return:
    """
    current_try = core_db.api.add_try_to_spammers(tg_id)
    assert current_try > 0

def test_check_user_priv():
    """
    Проверяем и добавляем пользователю привилегию
    :return:
    """
    assert core_db.api.check_user_in_privilege(tg_id)
    assert core_db.api.check_user_in_privilege(tg_id_dup)
    assert core_db.api.check_user_in_privilege(tg_id_not_dup)

def test_isDupUser():
    """
    Дубликаты пользователя
    :return:
    """
    assert core_db.api.is_user_dup(fio)
    assert not core_db.api.is_user_dup(fio_not_dup)


def test_aprove_user():
    """
    Подтверждаем пользователя
    :return:
    """
    assert core_db.api.approve_user(tg_id)


def test_isAprove():
    """
    Подтвержден ли пользователь
    :return:
    """
    assert core_db.api.is_user_approved(tg_id)
    assert not core_db.api.is_user_approved(tg_id_not_dup)
    assert not core_db.api.is_user_approved(tg_id_dup)


def test_update_priv():
    """
    Обновляем привелегии
    :return:
    """
    assert core_db.api.update_privilege(tg_id, 'supervisor', 1)

def test_update_user_info():
    """
    Обновляем атрибуты пользователя
    :return:
    """
    assert core_db.api.update_userinfo(tg_id, 'email', 'test@otr.ru')
    assert not core_db.api.update_userinfo(000000000, 'email', 'test@otr.ru')


def test_get_user_info():
    """
    Получаем информацию о пользователе
    :return:
    """
    assert isinstance(core_db.api.get_user_profile(tg_id), dict)
    assert not core_db.api.get_user_profile(000000000)
    assert core_db.api.get_user_profile(tg_id)['privilege']['supervisor'] == 1
    assert core_db.api.get_user_profile(tg_id_dup)['privilege']['supervisor'] == 0
    assert core_db.api.get_user_profile(tg_id_not_dup)['privilege']['supervisor'] == 0
    assert core_db.api.get_user_profile(tg_id)['email'] == 'test@otr.ru'

def test_isSupervisor():
    """
    Владеет ли пользователь полномочиями supervisor
    :return:
    """
    assert core_db.api.is_user_supervisor(tg_id)
    assert not core_db.api.is_user_supervisor(tg_id_dup)

def test_isRegUser():
    """
    Зареган ли пользак
    :return:
    """
    assert core_db.api.is_user_registered(tg_id)
    assert not core_db.api.is_user_registered(000000000)


def test_get_all_user_profiles():
    """
    Получаем информацию о всех пользователе
    :return:
    """

    all_users = core_db.api.get_all_user_profile()
    assert all_users
    assert isinstance(all_users, dict)
    assert all_users[tg_id]['privilege']
    assert all_users[tg_id_not_dup]['privilege']
    assert all_users[tg_id_dup]['privilege']
    assert all_users[tg_id]
    assert all_users[tg_id_not_dup]
    assert all_users[tg_id_dup]



def test_save_stats():
    """
    Сохраняем тестовую статистику
    :return:
    """

    assert core_db.api.save_stats('тест')

def test_get_stats():
    """
    Получаем статистику

    :return:
    """
    assert core_db.api.get_stats('day')
    assert core_db.api.get_stats('week')
    assert core_db.api.get_stats('month')
    assert core_db.api.get_stats('all')

def test_delete_user():
    """
    Удаляем пользователя
    :return:
    """
    assert core_db.api.delete_user(tg_id)
    assert core_db.api.delete_user(tg_id_dup)
    assert core_db.api.delete_user(tg_id_not_dup)
