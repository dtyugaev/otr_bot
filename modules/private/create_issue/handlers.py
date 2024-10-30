# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
from aiogram import types
from aiogram.dispatcher.filters import Text

from bot_core import states, filters
from core import resources
from . import create

"""

Хендлеры для модуля 'создать заявку'
"""

def init():
    resources.data.dp.register_message_handler(create.cancel, filters.IsUserApprove(), Text(equals="Отменить создание заявки", ignore_case=True), state="*")
    resources.data.dp.register_message_handler(create.get_subject, filters.IsUserApprove(), state=states.Processing_create_issue.wait_subject)
    resources.data.dp.register_message_handler(create.get_desc, filters.IsUserApprove(), state=states.Processing_create_issue.wait_desc, content_types=types.ContentType.ANY)
    resources.data.dp.register_callback_query_handler(create.get_accept, filters.IsUserApprove(), lambda c: 'accept_create_issue' in c.data, state=states.Processing_create_issue.wait_accept)
