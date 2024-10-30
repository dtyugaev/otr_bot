# -*- coding: utf-8 -*-


from core import resources
from . import module_list_issues

"""

Хендлеры для модуля 'список задач пользователя'
"""

def init():
    # вывод списка задач
    resources.data.dp.register_callback_query_handler(module_list_issues.get_all_issues, lambda c: 'issue:' in c.data)

