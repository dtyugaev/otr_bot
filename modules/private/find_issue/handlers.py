# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru


from aiogram.dispatcher.filters import Text

from bot_core import states
from core import resources
from modules.private.processing_issue import processing
from . import find_issue

"""

Хендлеры для модуля 'найти заявку по номеру'
"""


def init():
    resources.data.dp.register_message_handler(processing.cancel, Text(equals="Закончить работу с заявкой", ignore_case=True), state="*")
    resources.data.dp.register_message_handler(find_issue.cancel, Text(equals="Отмена", ignore_case=True), state="*")
    resources.data.dp.register_callback_query_handler(processing.close, lambda c: 'accept_issue' in c.data, state="*")
    resources.data.dp.register_callback_query_handler(processing.get_attach, lambda c: 'get_attach' in c.data, state="*")
    resources.data.dp.register_callback_query_handler(processing.wait_comment, lambda c: 'wait_comment' in c.data, state="*")
    resources.data.dp.register_callback_query_handler(processing.wait_reopen, lambda c: 'reopen_issue' in c.data, state="*")
    resources.data.dp.register_callback_query_handler(processing.wait_give_info, lambda c: 'give_info' in c.data, state="*")
    resources.data.dp.register_message_handler(find_issue.process_find_issue, state=states.Find_issue.enter_issue)
