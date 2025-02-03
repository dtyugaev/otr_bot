# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

import asyncio
import datetime
import json
import logging
import os

from aiogram import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

import service
from bot_core import handlers
from core import constant, resources, system

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration

_st = {'ver': constant.VERSION,
       'time_start': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

os.makedirs(constant.STORAGE, exist_ok=True)

with open(constant.STATUS_FILE, 'w') as file:
    json.dump(_st, file)


bot = resources.data.bot
dp = resources.data.dp


class UserEventsMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        if update.message:
            user = update.message.from_user
            logging.info(f"Message from user {user.id}: {update.message.text}")
        elif update.callback_query:
            user = update.callback_query.from_user
            logging.info(f"Callback query from user {user.id}: {update.callback_query.data}")
        elif update.inline_query:
            user = update.inline_query.from_user
            logging.info(f"Inline query from user {user.id}: {update.inline_query.query}")
        elif update.chosen_inline_result:
            user = update.chosen_inline_result.from_user
            logging.info(f"Chosen inline result from user {user.id}: {update.chosen_inline_result.result_id}")
        elif update.shipping_query:
            user = update.shipping_query.from_user
            logging.info(f"Shipping query from user {user.id}: {update.shipping_query.id}")
        elif update.pre_checkout_query:
            user = update.pre_checkout_query.from_user
            logging.info(f"Pre-checkout query from user {user.id}: {update.pre_checkout_query.id}")
        elif update.poll_answer:
            user = update.poll_answer.user
            logging.info(f"Poll answer from user {user.id}: {update.poll_answer.poll_id}")

dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(UserEventsMiddleware())

handlers.init(dp)  # инициируем все наши хендлеры
system.clear_temp_tables() # очищаем темповые таблицы в бд

async def on_startup(dp):
    """

    То что происходит после старта бота

    :param dp:
    :return:
    """
    logging.info('Бот запущен')
    loop = asyncio.get_event_loop()

    if os.getenv('otr_bot_debug') != 'true':
        loop.create_task(service.monitoring_issue.monitoring.monitoring()) # Запускаем мониторинг заявок (await не нужен. Так как иначе бесконечно будет ожидать)
    await bot.send_message(resources.data.config['Telegram']['approval_group_id'], 'Бот запущен', disable_notification=True)


async def on_shutdown(dp):
    logging.warning('Бот останавливается...')
    """
    То что происходит после остановки бота

    :param dp: 
    :return: 
    """
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning('Бот остановлен')

logging_integration = LoggingIntegration(
    level=logging.DEBUG
)

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=1.0,
integrations=[
            AsyncioIntegration(),
            logging_integration,
            StdlibIntegration(),

        ],
    attach_stacktrace=True,
    include_local_variables=True,
    send_default_pii=True,
    max_request_body_size="always"
)
if __name__ == '__main__':
    # Fix allowed_updates=types.AllowedUpdates.all() Теперь телеграмм заставляет указывать типы обновлений, которые мы хотим получать.
    # Но в 3 версии все само добавляется
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown, allowed_updates=types.AllowedUpdates.all())
