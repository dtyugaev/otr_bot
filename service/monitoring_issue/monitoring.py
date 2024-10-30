# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

import asyncio
import concurrent.futures
import logging
import typing
from jira import JIRA
import requests

from core import resources, core_modules, core_db
from . import keyboards

statused = {
    "10002": "Отложено",
    "10005": "Запрос информации",
    "10006": "Спам",
    "10017": "В работе",
    "10508": "Закрыто",
    "10900": "Зарегистрировано",
    "10901": "Ожидает решения",
    "10902": "Ответ предоставлен",
    "10903": "Предложено решение",
    "10904": "Переоткрыто",
    "12000": "Согласование ФЗ",
    "14200": "Передано на 3 линию",
    "14300": "Согласование УИБ",
    "14301": "Прокомментировано УИБ",
}


class Monitoring_issues:
    def __init__(self):
        self.events = list()
        self.all_notif = dict()
        self.have_error = False
        self.jira = resources.data.jira.jira
        self.cookies = self.coc()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'X-Atlassian-Token': 'no-check'
        }

    def coc(self):
        config_data = resources.data.config
        jira_options = {'server': config_data['jira']['url'], 'verify': False}
        jir = JIRA(options=jira_options, basic_auth=(config_data['jira']['login'], config_data['jira']['password']), async_=True)
        cookies = jir._session.cookies._cookies
        for k, v in cookies.items():
            for kk, vv in v.items():
                if isinstance(vv, dict):
                    kok = {'JSESSIONID': vv['JSESSIONID'].value, 'atlassian.xsrf.token': vv['atlassian.xsrf.token'].value}
                    self.cookies = kok
                    return kok
        raise Exception("Error get cookies jira")

    def logger(self, text, isError=False):
        if isError:
            logging.error("[monitoring] " + text)
        else:
            logging.info("[monitoring] " + text)

    def delete_event_id(self, id):
        self.logger(f"Попытка удаления ивента {id}")
        response = requests.delete(f'{resources.data.config["service"]["event_url"]}/{id}', cookies=self.cookies)
        if not response.status_code == 200:
            logging.fatal(response.text)
            logging.debug(f'cookies: {self.cookies}')
            new_coc = self.coc()
            logging.debug(f'new cookies: {str(new_coc)}')
            raise Exception("Bad responce code delete %s" % response.status_code)
        self.logger(f"Удален ивент {id}")


    def get_event(self):
        response = requests.get(resources.data.config["service"]["event_url"], cookies=self.cookies)
        if not response.status_code == 200:
            logging.fatal(response.text)
            logging.debug(f'cookies: {self.cookies}')
            new_coc = self.coc()
            logging.debug(f'new cookies: {str(new_coc)}')
            logging.info(response.text)
            raise Exception("Bad responce code event: %s" % response.status_code)
        res = response.json()
        if res:
            logging.debug(f'found events: {str(res)}')
        return res

    def generate_notification(self, events: typing.Dict) -> typing.Dict:
        notif = dict()

        for k, v in events.items():
            status = statused[v['statusId']]
            if status == 'Запрос информации':
                notif[k] = {'userName': v['userName'], 'message': 'запрошена дополнительная информация', 'reporterEmail': v['reporterEmail']}
            elif status == 'Предложено решение':
                notif[k] = {'userName': v['userName'], 'message': 'предложено решение', 'reporterEmail': v['reporterEmail']}

        if notif:
            logging.debug(f"saved notification: {str(notif)}")
        return notif

    def run(self) -> typing.Dict:
        self.logger("Собираем ивенты...")
        events = self.get_event()
        self.logger("Ивенты собраны")
        saved_events = dict()


        for i in events:
            saved_events[i['issueKey']] = i

        notif = self.generate_notification(saved_events)
        return notif


    async def send_notificate(self, notification: typing.Dict):
        """
        Отправляем уведомления пользователям

        :return:
        """

        if not notification:
            self.logger("Не найдены уведомления для отправки")
            return

        self.logger("Отправляем уведомления")
        for k, v in notification.items():
            logging.debug(f"Event data: {str(v)}")
            profile_data = core_db.api.get_user_profile_from_attr('email', v['reporterEmail'])
            if not profile_data:
                self.logger(f"Не найден профиль в бд {v['reporterEmail']}", isError=True)
                continue

            for i in profile_data:
                try:
                    await resources.data.bot.send_message(i['tg_id'], f"По заявке {k} {v['message']}", reply_markup=keyboards.kb_open_issue(k))
                except Exception:
                    logging.exception("Ошибка отправки сообщения для пользователя")
                    self.logger(f"Не удалось отправить сообщение для пользователя {i['tg_id']}", isError=True)

    async def delete_all_event(self) -> typing.List[str]:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            events = await loop.run_in_executor(pool, self.get_event)

        if not events:
            self.logger("Не найдены ивенты для удаления")
            return []

        errors = list()
        for i in events:
            try:
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    await loop.run_in_executor(pool, self.delete_event_id, i['id'])
            except Exception:
                logging.exception(f"Ошибка удаления ивента: {i['id']}")
                errors.append(f"Ошибка удаления ивента: {i['id']}")

        return errors

    async def send_errors(self, errors: typing.List):
        text = "⚠⚠⚠Найдены ошибки в мониторинге:\n\n"
        for i in errors:
            text += i + '\n'

        if len(text) > 4096:
            text = '⚠⚠⚠Найдены ошибки в мониторинге. Текст слишком большой, чтобы его отправить сюда, поэтому проверьте логи'

        await resources.data.bot.send_message(resources.data.config['Telegram']['approval_group_id'], text)


async def monitoring():
    mon = Monitoring_issues()
    loop = asyncio.get_running_loop()
    while True:
        try:

            with concurrent.futures.ThreadPoolExecutor() as pool:
                notif = await loop.run_in_executor(pool, mon.run)

            await mon.send_notificate(notif)
            errors_delete_events = await mon.delete_all_event()
            if errors_delete_events:
                await mon.send_errors(errors_delete_events)
            await asyncio.sleep(30)
        except Exception:
            logging.exception("Fatal error")
            await core_modules.send_logs(comment='Ошибка в мониторинге заявок')
            await asyncio.sleep(600)
            logging.info('restart monitoring')
