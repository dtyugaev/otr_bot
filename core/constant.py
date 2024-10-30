# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

import os

VERSION = '4.3.0'

# folders
WORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STORAGE = os.path.join(WORK_DIR, 'storage')
LOGS = os.path.join(WORK_DIR, 'logs')
TMP_DIR = os.path.join(WORK_DIR, 'tmp')

# files
DATABASE_FILE = os.path.join(STORAGE, 'data.sqlite')  # бд
SESSION = os.path.join(STORAGE, 'session')  # файл с кукисами
SERVICE_REBOOT_FILE = os.path.join(TMP_DIR, 'service.reboot')  # файл для уведомления о том, что сервис упал
CONFIG_FILE = os.path.join(WORK_DIR, 'config.ini')
STATUS_FILE = os.path.join(STORAGE, 'status')  # файл который хранит себе информацию о версии, времени запуска

# Статистика
STATS_ACTIONS = {'create_issue': 'Создание заявки',
                 'open_issue': 'Открыть заявку',
                 'proc_status': 'Изменить статус заявки',
                 'proc_comment': 'Добавить комментарий в заявку'}

ADMINS = [816666973, ]
