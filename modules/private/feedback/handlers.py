# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru
from aiogram import types
from aiogram.dispatcher.filters import Text

from bot_core import states
from core import resources
from . import feedback

"""
хендлеры для модуля обратной связи
"""





def init():
    resources.data.dp.register_message_handler(feedback.cancel, Text(equals="Отменить обращение", ignore_case=True), state="*")
    resources.data.dp.register_message_handler(feedback.hook_answer, state=states.Feedback.wait_answer, content_types=types.ContentType.ANY)
    resources.data.dp.register_message_handler(feedback.hook_message, state=states.Feedback.wait_message, content_types=types.ContentType.ANY)
    resources.data.dp.register_callback_query_handler(feedback.answer_message, lambda c: 'fb_answer' in c.data)
