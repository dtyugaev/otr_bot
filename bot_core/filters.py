# -*- coding: utf-8 -*-
from aiogram import types
from aiogram.dispatcher.filters import Filter

from core import core_db

"""
Фильтры для хендлеров
"""

class IsAdmin(Filter):
    key = "is_admin"
    async def check(self, message: types.Message):
        return True

class IsUserApprove(Filter):
    key = "is_user_approved"
    async def check(self, message: types.Message):
        return core_db.api.is_user_approved(message.from_user.id)


class IsUserSpammer(Filter):
    key = "is_user_spammer"
    async def check(self, message: types.Message):
        return core_db.api.is_user_spammer(message.from_user.id)