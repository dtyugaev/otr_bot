# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text

import modules
import service
from core import resources
from . import filters

"""
Модуль для хранения хендлеров
"""

def init_modules():
    #services
    service.monitoring_issue.handlers.init()

    #private
    modules.private.feedback.handlers.init()
    modules.private.find_issue.handlers.init()
    modules.private.list_issues.handlers.init()
    modules.private.my_profile.handlers.init()
    modules.private.processing_issue.handlers.init()
    modules.private.reg_user.handlers.init()
    modules.private.status_issue.handlers.init()
    modules.private.create_issue.handlers.init()

    #admins
    modules.admin.broadcast.handlers.init()
    modules.admin.send_user_message.handlers.init()



def init(dp: Dispatcher):
    APPROVAL_GROUP_ID = resources.data.config['Telegram']['approval_group_id']
    init_modules()

    #admins
    dp.register_message_handler(modules.admin.list_users.get_users.get_all_users, chat_id=APPROVAL_GROUP_ID, commands="list_users", state="*")
    dp.register_message_handler(modules.admin.get_logs.get_logs.get_logs, chat_id=APPROVAL_GROUP_ID, commands="get_logs", state="*")
    dp.register_message_handler(modules.admin.export_users.get_users.hook, chat_id=APPROVAL_GROUP_ID, commands="get_users", state="*")
    dp.register_message_handler(modules.admin.get_audit.hook.check_args, chat_id=APPROVAL_GROUP_ID, commands="get_audit", state="*")
    dp.register_message_handler(modules.admin.get_stats.start.get_all_stats, chat_id=APPROVAL_GROUP_ID, commands="stat", state="*")
    dp.register_message_handler(modules.admin.send_user_message.send.send, chat_id=APPROVAL_GROUP_ID, commands="senduser", state="*")
    dp.register_message_handler(modules.admin.broadcast.broadcast.get_mes, chat_id=APPROVAL_GROUP_ID, commands="broadcast", state="*")
    dp.register_message_handler(modules.admin.set_privilege.set_priv.install_privilege, chat_id=APPROVAL_GROUP_ID, commands="install_priv", state="*")
    dp.register_message_handler(modules.admin.set_privilege.set_priv.remove_privilege, chat_id=APPROVAL_GROUP_ID, commands="remove_priv", state="*")

    #common
    dp.register_message_handler(modules.common.help.module_help.cmd_help, commands="help", state="*")
    dp.register_message_handler(modules.common.status.get_status.get_status, commands="status", state="*")

    #private
    dp.register_message_handler(modules.private.start.module_private_start.cmd_start, commands="start", chat_type=types.ChatType.PRIVATE, state="*")
    dp.register_message_handler(modules.private.reg_user.module_private_reg_user.start, commands="regme", chat_type=types.ChatType.PRIVATE, state="*")
    dp.register_message_handler(modules.private.my_profile.start.my_profile, filters.IsUserApprove(), Text(equals="Мой профиль", ignore_case=True), state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(modules.private.feedback.feedback.start, filters.IsUserApprove(), Text(equals="Обратная связь", ignore_case=True), state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(modules.private.status_issue.start.generate_choise, filters.IsUserApprove(), Text(equals="Узнать статус заявки", ignore_case=True), state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(modules.private.create_issue.create.start, filters.IsUserApprove(), Text(equals="Создать заявку", ignore_case=True), state="*", chat_type=types.ChatType.PRIVATE)
