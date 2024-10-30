# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from bot_core import states
from core import resources
from . import send

"""

Хендлеры для модуля отправки сообщений пользователю
"""


def init():
    resources.data.dp.register_callback_query_handler(send.accept_send, lambda query: 'accept_send' in query.data, state=states.Send_admin_message.wait_send)
