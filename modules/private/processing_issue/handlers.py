# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types

from bot_core import states
from core import resources
from . import processing

"""

Хендлеры для модуля 'операция с заявками'
"""


def init():
    resources.data.dp.register_message_handler(processing.add_comment, state=states.Processing_issue_comment.wait_comment, content_types=types.ContentType.ANY)
    resources.data.dp.register_message_handler(processing.give_info, state=states.Processing_issue_comment.wait_give_info, content_types=types.ContentType.ANY)
    resources.data.dp.register_message_handler(processing.reopen, state=states.Processing_issue_comment.wait_reopen, content_types=types.ContentType.ANY)
