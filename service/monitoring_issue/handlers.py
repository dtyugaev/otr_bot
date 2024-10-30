# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

"""
хендлеры для модуля мониторинга заявок
"""

from core import resources
from modules.private import find_issue


def init():
    resources.data.dp.register_callback_query_handler(find_issue.find_issue.process_find_issue, lambda query: 'open_i_m' in query.data)