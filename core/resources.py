# -*- coding: utf-8 -*-
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from sqlite3 import Connection as sqlite_connection

from . import config
from . import core_jira
from . import core_db

"""
Общие ресурсы. Для взаимодействия с ними из других модулей

"""


class Resources:
    def __init__(self):
        self.config = config.load_config()
        self.bot = Bot(token=self.config['Telegram']['token'], timeout=300)
        loop = asyncio.get_event_loop()
        _b_info = loop.run_until_complete(self._get_bot_info())
        self.bot_data = _b_info.values
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.jira = core_jira.api.Api()
        self.DB: sqlite_connection = core_db.api.GetSession().get_session()
        logging.info("Ресурсы инициализированы")

    async def _get_bot_info(self):
        return await self.bot.get_me()


data = Resources()
