# -*- coding: utf-8 -*-

from core import resources
from modules.private import find_issue, list_issues

"""
Хендлеры для 'Список заявок'

"""


def init():
    # Найти заявку по номеру
    resources.data.dp.register_callback_query_handler(find_issue.find_issue.find, lambda c: c.data == 'find_issue_number')

    # вывод списка задач
    resources.data.dp.register_callback_query_handler(list_issues.module_list_issues.get_all_issues, lambda c: c.data == 'list_my_issue')