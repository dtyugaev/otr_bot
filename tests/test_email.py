# -*- coding: utf-8 -*-

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from core import constant, system, resources

"""

Тесты для отправки писем на почтовик otr.ru

"""

rotate = logging.handlers.RotatingFileHandler(os.path.join(constant.LOGS, 'log_test_email.txt'), maxBytes=10000000,
                                              backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG, handlers=[rotate, consoleHandler])

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.info("\nStart test")


def test_send_email():
    assert system.send_email(['emelin.petr@otr.ru'], 'Тестовое письмо тема', 'Тестовое письмо тело')
