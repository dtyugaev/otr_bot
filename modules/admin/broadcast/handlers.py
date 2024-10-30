# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from bot_core import states
from core import resources
from . import broadcast

"""

Хендлеры для модуля отправки сообщений пользователю
"""


def init():
    resources.data.dp.register_callback_query_handler(broadcast.accept, lambda query: 'accept_send' in query.data, state=states.Broadcast.wait_accept)
