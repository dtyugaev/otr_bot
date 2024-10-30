# -*- coding: utf-8 -*-

import configparser
import os
import typing

from . import constant


def load_config() -> typing.Dict[str, typing.Dict[str, typing.Union[str, typing.List[int]]]]:
    """
    Загрузка конфига

    :return:
    """
    if not os.path.isfile(constant.CONFIG_FILE):
        save_config()
        raise Exception("Created new config file: %s" % constant.CONFIG_FILE)

    config = configparser.ConfigParser()
    config.read(constant.CONFIG_FILE)
    sections = config.sections()
    for s in sections:
        for o in config.options(s):
            if not config.get(s, o):
                raise Exception(f"Empty {o} parameter in {s} section from config file")

    _admins = list()
    admins = config.get('Telegram', 'admins').split(',')
    for i in admins:
        try:
            int(i)
            _admins.append(int(i))
        except Exception:
            raise Exception("Bad parameter admins in config file. Must be: 12345,123456,1234567")

    config_dict = {s: dict(config.items(s)) for s in config.sections()}
    config_dict['Telegram'].update({'admins': _admins})
    try:
        config_dict['Telegram'].update({'approval_group_id': int(config_dict['Telegram']['approval_group_id'])})
    except ValueError:
        raise Exception("Bad parameter approval_group_id in config file. Must be interger")

    if config_dict['jira']['url'].endswith("/"):
        config_dict['jira']['url'] = config_dict['jira']['url'][:-1]

    if config_dict['service']['event_url'].endswith("/"):
        config_dict['service']['event_url'] = config_dict['service']['event_url'][:-1]

    return config_dict

def save_config() -> bool:
    """
    Создание конфига

    :return:
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "debug", "false")
    config.add_section("Telegram")
    config.set("Telegram", "token", "")
    config.set("Telegram", "admins", "")
    config.set("Telegram", "approval_group_id", "")
    config.add_section("jira")
    config.set("jira", "url", "")
    config.set("jira", "login", "")
    config.set("jira", "password", "")
    config.add_section("service")
    config.set("service", "event_url", "")

    with open(constant.CONFIG_FILE, "w") as config_file:
        config.write(config_file)
    return True