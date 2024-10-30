# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram.dispatcher.filters import Text

from bot_core import states, filters
from core import resources
from . import start

"""
хендлеры для модуля Мой профиль
"""


def init():
    resources.data.dp.register_message_handler(start.cancel, filters.IsUserApprove(), Text(equals="Завершить работу с профилем", ignore_case=True), state="*")
    resources.data.dp.register_callback_query_handler(start.hook_del, lambda c: 'prof:del' == c.data)
    resources.data.dp.register_callback_query_handler(start.del_profile, lambda c: 'prof' in c.data, state=states.My_profile.del_profile)

    # #security.init.dp.register_message_handler(start.hook_message, state=all_states.Feedback.wait_message, content_types=types.ContentType.ANY)
    # #security.init.dp.register_message_handler(feedback.hook_answer, state=all_states.Feedback.wait_answer, content_types=types.ContentType.ANY)
    # security.init.dp.register_callback_query_handler(start.hook_edit, lambda c: 'prof:edit' == c.data)
    # security.init.dp.register_callback_query_handler(start.edit_profile, lambda c: 'edit' in c.data, state=states.My_profile.edit_profile)
    # security.init.dp.register_callback_query_handler(start.selected_new_atr_region, lambda c: 'regu' in c.data, state=states.My_profile.wait_new_atr_region)
    # security.init.dp.register_callback_query_handler(start.accept_new_atr, lambda c: 'prof' in c.data, state=states.My_profile.wait_new_atr_accept)
    # security.init.dp.register_message_handler(start.selected_new_atr, state=states.My_profile.wait_new_atr)
