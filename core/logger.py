# -*- coding: utf-8 -*-
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from . import constant

"""
Инициализация логгера

"""


os.makedirs(constant.LOGS, exist_ok=True)
# 10000000Bytes ~ 10MB .
rotate = logging.handlers.RotatingFileHandler(os.path.join(constant.LOGS, 'log.txt'), maxBytes=10000000,
                                              backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)
#todo определение уровня логгирования относительно конфига
logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)", level=logging.DEBUG, handlers=[rotate, consoleHandler])
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.info("\nStart v {}".format(constant.VERSION))
