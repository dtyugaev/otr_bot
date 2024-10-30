# -*- coding: utf-8 -*-


import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import pytest

import service
from core import resources, constant

"""

Тесты для сервиса мониторинга заявок

"""

rotate = logging.handlers.RotatingFileHandler(os.path.join(constant.LOGS, 'log_test_service_monitoring.txt'), maxBytes=10000000,
                                              backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG, handlers=[rotate, consoleHandler])

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.info("\nStart test")

jira = resources.data.jira

monitoring = service.monitoring_issue.monitoring.Monitoring_issues()

def test_get_events():
    events = monitoring.get_event()
    assert events

def test_delete_event():
    events = monitoring.get_event()
    monitoring.delete_event_id(events[0]['id'])
    new_events = monitoring.get_event()
    assert len(events) > len(new_events)

def test_run():
    assert monitoring.run()

@pytest.mark.asyncio
async def test_send_notifications():
    notif = monitoring.run()
    await monitoring.send_notificate(notif)

