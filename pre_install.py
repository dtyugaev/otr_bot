# -*- coding: utf-8 -*-
import sqlite3
import os
import asyncio
from core import constant, resources
import logging
"""
Инициализация необходимых ресурсов перед первым запуском бота

"""
version = '0.1'

logging.info(f"Start pre install script version: {version}")
init_dirs = (constant.LOGS, constant.STORAGE,)
for i in init_dirs:
    os.makedirs(i, exist_ok=True)

if not os.path.isfile(constant.DATABASE_FILE):
    logging.warning("Not found database. Create new...")
    DB = sqlite3.connect(constant.DATABASE_FILE)
    cur = DB.cursor()
    sql_file = open("update/database_create.sql")
    sql_as_string = sql_file.read()
    cur.executescript(sql_as_string)
    #todo приделать проверку
    logging.info("Database created")

logging.info("complete")

async def quit():
    await resources.data.dp.storage.close()
    await resources.data.dp.storage.wait_closed()
    await resources.data.bot.session.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(quit())

