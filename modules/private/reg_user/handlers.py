# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru


from aiogram.dispatcher.filters import Text

from bot_core import states, filters
from core import resources
from . import module_private_reg_user

"""

Хендлеры для модуля регистрации пользователей
"""


def init():
    resources.data.dp.register_message_handler(module_private_reg_user.cancel, Text(equals="Отмена регистрации", ignore_case=True), state="*")
    resources.data.dp.register_message_handler(module_private_reg_user.spam, filters.IsUserSpammer(), state="*")
    resources.data.dp.register_callback_query_handler(module_private_reg_user.spam, filters.IsUserSpammer(), state="*")
    resources.data.dp.register_message_handler(module_private_reg_user.add_email, state=states.Register_process.wait_email)
    resources.data.dp.register_message_handler(module_private_reg_user.add_code, state=states.Register_process.wait_code)
    resources.data.dp.register_callback_query_handler(module_private_reg_user.recode, lambda query: 'recode' in query.data, state="*")


    # security.init.dp.register_message_handler(module_private_reg_user.add_inn, state=states.Register_process.wait_org_inn)
    # security.init.dp.register_message_handler(module_private_reg_user.add_email, state=states.Register_process.wait_email)
    # security.init.dp.register_message_handler(module_private_reg_user.add_phone, state=states.Register_process.wait_phone)
    # security.init.dp.register_message_handler(module_private_reg_user.add_etd_login, state=states.Register_process.wait_etd_login)
    # security.init.dp.register_message_handler(module_private_reg_user.fail_admin_reg, state=states.Register_process.wait_fail_comment)

    # security.init.dp.register_callback_query_handler(module_private_reg_user.accept_admin_reg, lambda query: 'aprove_mode' in query.data, state="*")