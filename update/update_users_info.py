# -*- coding: utf-8 -*-

import asyncio
import logging
import os
import sqlite3
import sys
from logging.handlers import RotatingFileHandler

from core import core_modules, constant

if os.path.isfile('log_update_users.txt'):
    os.remove('log_update_users.txt')

rotate = logging.handlers.RotatingFileHandler('log_update_users.txt', maxBytes=10000000,
                              backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="%(message)s",
                    level=logging.INFO, handlers=[rotate, consoleHandler])

VERSION = '0.5'
logging.info("START %s" % VERSION)
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
db = sqlite3.connect(constant.DATABASE_FILE_PATH)
db.row_factory = dict_factory
cur = db.cursor()

cur.execute("select * from users")
result = cur.execute("select * from users")
res = result.fetchall()

if not res:
    raise Exception("not found users")

errors = list()
complete = list()
complete_error = list()

r = cur.execute("PRAGMA table_info(users);")
logging.info(r.fetchall())
logging.info("USING DB: %s" % constant.DATABASE_FILE_PATH)
logging.info("TOTAL USERS: %s" % len(res))

async def main():
    for i in res:
        _e = 0
        logging.info(f"Try: {i['etd_login']} ...")

        data = await core_modules.doms_get_data_org(i['etd_login'])
        logging.info(f"data for {i['etd_login']}: {str(data)}")
        if not data:
            errors.append("Empty data for %s" % i['etd_login'])
            logging.error("Empty data for %s" % i['etd_login'])
            continue

        if 'CodeMo' not in data.keys():
            errors.append(f"Not found CodeMo for {i['etd_login']}")
            logging.error(f"Not found CodeMo for {i['etd_login']}")
            _e += 1
        else:
            if str(data['CodeMo']).startswith('99'):
                cur.execute("UPDATE users SET CodeMo=? WHERE tg_id=?", (data['CodeMo'], i['tg_id']))
            else:
                logging.warning(f"bad CodeMo for {i['etd_login']}: {data['CodeMo']}")
                _e += 1

        if 'RootCodeMo' not in data.keys():
            errors.append(f"Not found RootCodeMo for {i['etd_login']}")
            logging.error(f"Not found RootCodeMo for {i['etd_login']}")
            _e += 1
        else:
            if str(data['RootCodeMo']).startswith('99'):
                cur.execute("UPDATE users SET RootCodeMo=? WHERE tg_id=?", (data['RootCodeMo'], i['tg_id']))
            else:
                logging.warning(f"bad RootCodeMo for {i['etd_login']}: {data['RootCodeMo']}")
                _e += 1


        db.commit()

        if _e == 0:
            complete.append(i['etd_login'])
        elif _e == 1:
            complete_error.append(i['etd_login'])
        else:
            pass

    if errors:
        for i in errors:
            logging.error(i + '\n\n')
        print("Found errors")

    logging.info(f"COMPLETE: {complete}")
    logging.info(f"COMPLETE THIS ERRORS: {complete_error}")
    print(f"COMPLETE: {len(complete)}")
    print(f"COMPLETE THIS ERRORS: {len(complete_error)}")



loop = asyncio.get_event_loop()
results = loop.run_until_complete(main())