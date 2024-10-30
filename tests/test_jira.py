# -*- coding: utf-8 -*-


import datetime
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import pytest

from core import resources, constant

"""

Тесты для джиры

"""



rotate = logging.handlers.RotatingFileHandler(os.path.join(constant.LOGS, 'log_test_jira.txt'), maxBytes=10000000,
                                              backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG, handlers=[rotate, consoleHandler])

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.info("\nStart test")

jira = resources.data.jira

tg_id = 816666973
issue_id = 'IT-55237'
email = 'yasinskii_aa@proitr.ru'



@pytest.fixture()
def create_status_file():
    _st = {'ver': constant.VERSION,
           'time_start': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

    with open(constant.STATUS_FILE, 'w') as file:
        json.dump(_st, file)

def test_search_user():
    """
    Поиск пользователя
    :return:
    """
    fio = 'Емелин Петр Алексеевич'
    res = resources.data.jira.jira.search_users(email, maxResults=99999)
    found_user = None
    for i in res.iterable:
        if i.emailAddress == email:
            found_user = i
            break

    assert found_user
    assert found_user.displayName == fio


def test_create_issue(create_status_file):
    """
    Регистрация заявки
    """
    project = 'IT'
    subject = 'bot test subject'
    desc = 'bot test desc'
    issue_key = jira.create_issue(project=project, subject=subject, id=tg_id, desc=desc)
    print(issue_key)
    assert issue_key

def test_add_comment(create_status_file):
    """
    Добавление комментария в заявку

    :return:
    """
    assert jira.add_comments(comment='тестовый комментарий', id=issue_id)

def test_add_comment_attach(create_status_file):
    """
    Добавление комментария в заявку с приложением

    :return:
    """
    assert jira.add_comments(comment='тестовый комментарий с аттачем', id=issue_id, attach=constant.STATUS_FILE)


def test_get_attachment(create_status_file):
    """
    Получение аттачей из заявки

    :return:
    """
    file_name = jira.get_issue_attachments_file(issue_id)
    assert os.path.isfile(file_name)
    os.remove(file_name)


def test_switch_status_to_wait_info(create_status_file):
    """
    Смена статуса на 'запрос информации'

    Не учавствует в логиге, но позволит автоматизировать тесты

    :return:
    """
    result = jira.switch_status(action='Запросить информацию', id=issue_id, comment='Дай инфу плс')
    assert result == 0


def test_give_information(create_status_file):
    """
    Предоставить информацию

    :return:
    """
    result = jira.switch_status(action='Ответить', id=issue_id, comment='Вот тебе информация')
    assert result == 0

def test_give_information_this_attach(create_status_file):
    """
    Предоставить информацию c аттачем

    :return:
    """
    result = jira.switch_status(action='Запросить информацию', id=issue_id, comment='Дай инфу плс')
    assert result == 0

    result = jira.switch_status(action='Ответить', id=issue_id, comment='Вот тебе информация', attach=constant.STATUS_FILE)
    assert result == 0

def test_give_solution(create_status_file):
    """
    Предоставить решение

    Не учавствует в логике. Нужно для автоматизации тестов
    :return:
    """
    try:
        result = jira.switch_status(action='В работу', id=issue_id, comment='Вот тебе решение')
        assert result == 0
    except Exception:
        pass

    result = jira.switch_status(action='Решение', id=issue_id, comment='Вот тебе решение')
    assert result == 0

def test_reopen(create_status_file):
    """
    Переоткрыть заявку

    :return:
    """
    result = jira.switch_status(action='Переоткрыть', id=issue_id, comment='Переоткрываю')
    assert result == 0

def test_reopen_this_attach(create_status_file):
    """
    Переоткрыть заявку с аттачем

    :return:
    """
    try:
        result = jira.switch_status(action='В работу', id=issue_id, comment='Беру в работу')
        assert result == 0
    except Exception:
        pass

    result = jira.switch_status(action='Решение', id=issue_id, comment='Вот тебе решение')
    assert result == 0

    result = jira.switch_status(action='Переоткрыть', id=issue_id, comment='Переоткрываю с аттачем', attach=constant.STATUS_FILE)
    assert result == 0

def test_close():
    """

    Закрыть заявку
    :return:
    """
    try:
        result = jira.switch_status(action='В работу', id=issue_id, comment='Беру в работу')
        assert result == 0
    except Exception:
        pass

    result = jira.switch_status(action='Решение', id=issue_id, comment='Вот тебе решение')
    assert result == 0

    result = jira.switch_status(action='Закрыть', id=issue_id, comment='Закрываю')
    assert result == 0

def test_close_this_attach(create_status_file):
    """

    Закрыть заявку
    :return:
    """
    try:
        result = jira.switch_status(action='Переоткрыть', id=issue_id, comment='Переоткрываю')
        assert result == 0
    except Exception:
        pass

    try:
        result = jira.switch_status(action='В работу', id=issue_id, comment='Беру в работу')
        assert result == 0
    except Exception:
        pass

    result = jira.switch_status(action='Решение', id=issue_id, comment='Вот тебе решение')
    assert result == 0

    result = jira.switch_status(action='Закрыть', id=issue_id, comment='Закрываю с аттачем', attach=constant.STATUS_FILE)
    assert result == 0


def test_get_issue(create_status_file):
    """
        получение данных заявки
    """
    issue_data = jira.get_issue_from_id(issue_id)
    assert issue_data


def test_get_issue_for_user():
    """
    Получение заявок для пользвателя по его email


    :return:
    """
    issues = jira.get_all_user_issues(email)
    for i in issues:
        for ii in i:
            print(ii.key, ii.fields.status.name)
        print("\n\n")
    assert issues