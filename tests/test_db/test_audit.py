# -*- coding: utf-8 -*-
import core
import logging
from random import randint


test_name = 'audit'
logging.info(f"\nStart test_{test_name}")

"""
Тестирование аудита

"""
tg_id = 816666973 # существующий в таблице users

test_audit_action = 'test_audit' + str(randint(0, 999))


def test_add_audit():
    """
    Добавляем аудит

    :return:
    """
    core.core_db.api.add_audit(tg_id, test_audit_action)
    core.core_db.api.add_audit(tg_id + 123, test_audit_action)


def test_get_audit():
    """
    Получаем аудит

    :return:
    """
    assert core.core_db.api.get_audit()
    assert core_db.api.get_audit(tg_id, 5)
    assert core_db.api.get_audit(tg_id)
    assert not core_db.api.get_audit(tg_id_dup, 5)
    assert not core_db.api.get_audit(tg_id_not_dup, 5)
