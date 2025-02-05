# -*- coding: utf-8 -*-

import datetime
import html
import logging
import re
import typing

from jira import JIRA
import sentry_sdk
from sentry_sdk.tracing import Transaction

from core import config, core_db, system


class GetInstance:
    def __init__(self):
        self.jira = None
        self.config_data = config.load_config()
        self.auth()
        """
        Запросить информацию -> запрос информации
        Из: В работе, Ответ предоставлен

        Ответить -> Ответ предоставлен
        Из: запрос информации

        Решение -> Предложено решение
        Из: В работе,

        Переоткрыть -> Переоткрыто
        Из: Предложено решение
        
        Закрыть -> Закрыто
        Из: Предложено решение
        """
        self.complete_switch_statused = {'Запросить информацию':
                                             {'new_status': 'Запрос информации',
                                              'from_status': ('В работе', 'Ответ предоставлен')
                                              },
                                         'Ответить':
                                             {'new_status': 'Ответ предоставлен',
                                              'from_status': ('Запрос информации',)
                                              },
                                         'Ответ для робота':
                                             {'new_status': 'Ответ предоставлен',
                                              'from_status': ('Запрос информации',)
                                              },
                                         'Предложено решение':
                                             {'new_status': 'Запрос информации',
                                              'from_status': ('В работе',)
                                              },
                                         'Решение':
                                             {'new_status': 'Предложено решение',
                                              'from_status': ('В работе', 'Ответ предоставлен')
                                              },
                                         'Переоткрыть':
                                             {'new_status': 'Переоткрыто',
                                              'from_status': ('Предложено решение', 'Закрыто')
                                              },
                                         'Закрыть':
                                             {'new_status': 'Закрыто',
                                              'from_status': ('Предложено решение',)
                                              },
                                         'В работу':
                                             {'new_status': 'В работе',
                                              'from_status': ('Переоткрыто', 'Ответ предоставлен')
                                              },
                                         }

    def auth(self):
        jira_options = {'server': self.config_data['jira']['url'], 'verify': False}
        logging.info("Try connect to: %s" % jira_options)
        self.jira = JIRA(options=jira_options, basic_auth=(self.config_data['jira']['login'], self.config_data['jira']['password']), async_=True)
        self.all_fields = self.jira.fields()
        logging.info(f"Jira connected to {jira_options['server']}")

    def custom_field(self, tg_id, project, subject, description) -> typing.Dict:
        fields = dict()
        # test_fields = dict()
        # for i in self.all_fields:
        #     test_fields[i['id']] = i['name']

        for i in self.all_fields:
            fields[i['name']] = i['id']
        profile_data = core_db.api.get_user_profile(tg_id)
        # users_jira = self.jira.search_users(profile_data['email'])
        field_for_create = {
            "IT": {
                "project": "IT",
                "issuetype": {'id': '10000'},
                "summary": subject,
                "description": description,
                "reporter": {'name': profile_data['login']}
            },

        }

        return field_for_create[project]


class Api(GetInstance):
    def cookies_jira(self) -> typing.Dict:
        """
        Получение печенек авторизации из либы
        """
        cookies = self.jira._session.cookies._cookies
        for k, v in cookies.items():
            for kk, vv in v.items():
                if isinstance(vv, dict):
                    return {'JSESSIONID': vv['JSESSIONID'].value, 'atlassian.xsrf.token': vv['atlassian.xsrf.token'].value}
        raise Exception("Error get cookies jira")

    def create_issue(self, project: str, subject: str, desc: str, id: int, attach=None) -> str:
        """
        Регистрация заявки

        :param subject:
        :param project:
        :param desc:
        :param id:
        :param attach:
        :return:
        """

        new_issue = self.jira.create_issue(fields=self.custom_field(tg_id=id, project=project, subject=subject, description=desc))
        if attach:
            with open(attach, 'rb') as f:
                self.jira.add_attachment(issue=new_issue.key, attachment=f)
            while True:
                rem = system.remove_file(attach)
                if rem == None:
                    break
                elif rem == True:
                    break

        return new_issue.key

    def get_all_user_issues(self, email: str):
        """
            Метод получает из JIRA список задач по ФИО пользователя

        """

        jql_st = f'project in (IT) AND reporter in ({email.split("@")[0]}) ORDER BY createdDate'
        logging.debug("Used jql: %s" % jql_st)

        found_issues = self.jira.search_issues(jql_st)
        if found_issues.total == 0:
            return None

        """
        запрос инфо
        решен
        открыт
        в работе
        закрыт
        """

        """
        Заявки должны сортироваться сначала по статусу (сначала Запрос информации, далее Решен, далее все рабочие статусы, далее Закрыт), 
        а потом по дате создания – новые сверху.
        
        """

        information_request = list()  # запрос информации
        solved = list()  # решено
        open = list()  # открыт
        in_work = list()  # в работе
        closed = list()  # закрыто
        other = list()  # неизвестное
        total_collect = list()  # общее

        for issue in found_issues:
            status = issue.fields.status.name
            # logging.debug("Issue: %s now status: %s" % (issue.key, issue.fields.status.name))
            if status == 'Запрос информации':
                information_request.append(issue)
            elif status == 'Предложено решение':
                solved.append(issue)
            elif status == 'Открыта':
                open.append(issue)
            elif 'В работе' in status:
                in_work.append(issue)
            elif status == 'Закрыто':
                # closed.append(issue)
                pass
            else:
                other.append(issue)

        for i in information_request:
            total_collect.append(i)

        for i in solved:
            total_collect.append(i)

        for i in open:
            total_collect.append(i)

        for i in in_work:
            total_collect.append(i)

        for i in other:
            total_collect.append(i)

        for i in closed:
            total_collect.append(i)

        # split all issues in chunks
        total_collect_split_pages = [total_collect[i:i + 5] for i in
                                     range(0, len(total_collect), 5)]

        # logging.debug(total_collect_split_pages)
        return total_collect_split_pages

    def _get_comment_obj(self, comments: list):
        """
        Возвращает последние 15 комментов. В нашем случае коммент должен быть виден для всех
        :param comments:
        :return:
        """

        comment_list = list()
        for i in comments:
            if hasattr(i, 'visibility'):
                continue
            else:
                comment_list.append(i)
        return comment_list[-15:]

    def formatter_text(self, text):
        """
        Очищает текст от хлама

        :param text:
        :return:
        """
        # удаление {color} тегов

        cleanr = re.compile('{color(:\s*([^}]+))?}')
        text = re.sub(cleanr, '', text)

        return text

    def get_issue_from_id(self, id: str) -> typing.Dict:
        """
        Возвращает информаццию по заявке

        :param id:
        :return:
        """
        id = id.upper()

        try:
            issue = self.jira.issue(id, expand='renderedFields')
        except Exception:
            logging.exception(f"Ошибка получения информации по заявке: {id}")
            return {}

        _cr = datetime.datetime.strftime(datetime.datetime.strptime(issue.fields.created.split('.')[0], '%Y-%m-%dT%H:%M:%S'), '%d.%m.%Y %H:%M:%S')
        _up = datetime.datetime.strftime(datetime.datetime.strptime(issue.fields.updated.split('.')[0], '%Y-%m-%dT%H:%M:%S'), '%d.%m.%Y %H:%M:%S')

        _comm_list = list()

        if issue.fields.comment.total > 0:
            _l_comments = self._get_comment_obj(issue.fields.comment.comments)
            if not _l_comments:
                # бывает, если комменты есть, но они скрыты
                _comm_list = ('Комментарии к запросу еще не добавлены')
                comments_list = list()
            else:
                comments_list = list()
                #for comment in _l_comments:
                comment = _l_comments[-1]
                _comm_time_cr = datetime.datetime.strptime(comment.created.split('.')[0], '%Y-%m-%dT%H:%M:%S')

                _comm_render_text = html.escape(comment.body)
                _comm_list.append(f"<code>{datetime.datetime.strftime(_comm_time_cr, '%d.%m.%Y %H:%M')}</code>\n {_comm_render_text}")
                comments_list.append(f"<code>{datetime.datetime.strftime(_comm_time_cr, '%d.%m.%Y %H:%M')}</code>\n {_comm_render_text}")
                # _comm_list.reverse()
                # comments_list.reverse()
                _comm_list = '\n\n'.join(_comm_list)
        else:
            _comm_list = ('Комментарии к запросу еще не добавлены')
            comments_list = list()

        return {
            'Автор': issue.fields.reporter.name,
            'email': issue.fields.reporter.emailAddress,
            'Номер заявки': issue.key,
            'Дата создания': _cr,
            'Дата обновления': _up,
            'Тема заявки': html.escape(issue.fields.summary),
            'Описание заявки': self.formatter_text(html.escape(issue.fields.description)) if issue.fields.description else 'Описание не указано',
            'Текущий статус': issue.fields.status.name,
            'Комментарии': _comm_list,
            'comment_list': comments_list,
            'Количество вложений': len(issue.fields.attachment)
        }

    def add_comments(self, comment: str, id: str, attach=None, transaction_sentry: Transaction=None) -> bool:
        """


        :param comment: строка комментария
        :param attach: путь до файла
        :return:
        """
        if transaction_sentry is not None:
            transaction = transaction_sentry
        else:
            transaction = sentry_sdk.start_transaction(op='http.client', name='add_comments')

        with transaction.start_child(op='http.client', description='add_comment') as trans2:
            status_add = self.jira.add_comment(id, comment, )
            if not status_add:
                raise Exception(f"Empty result add comment to issue: {id}")

            if attach:
                with open(attach, 'rb') as f:
                    self.jira.add_attachment(issue=id, attachment=f)
                while True:
                    rem = system.remove_file(attach)
                    if rem is None:
                        break
                    elif rem:
                        break
            trans2.set_status('ok')
            trans2.finish()

        if transaction_sentry is None:
            transaction.set_status('ok')
            transaction.finish()
        return True

    def get_issue_attachments_file(self, issue_key):
        """
        Возвращает путь к архиву с вложениями
        """
        return system.zip_file(self.jira.issue(issue_key).fields.attachment)

    def switch_status(self, action: str, id: str, comment: str, attach=None) -> int:
        """
        Перевести заявку в другой статус

        :param action:
        :param id:
        :param comment:
        :param attach:
        :return:
        """

        logging.info(f"Попытка сменить статус {id} на {action} с комментарием: '{comment}' и аттачами: {str(attach)}")
        if action not in self.complete_switch_statused.keys():
            logging.info(f"Accept statused: {list(self.complete_switch_statused.keys())}. Try switch to: {action}")
            raise Exception(f"Invalid new status: {action}")

        issue = self.jira.issue(id)



        with sentry_sdk.isolation_scope() as scope:
            scope.set_context('issue_meta', {'id': id, 'status': issue.fields.status.name})
            with scope.start_transaction(op='http.client', name='switch_status') as trans:
                with trans.start_child(op='http.client', description='get transitions') as trans2:
                    # получаем список доступных переходов для текущего статуса
                    list_all_aviable_trans = self.jira.transitions(id)
                    trans2.set_data('response', {'issue_id': id, 'transactions available': list_all_aviable_trans})
                    trans2.set_status('ok')
                    trans2.finish()





                if issue.fields.status.name not in self.complete_switch_statused[action]['from_status']:
                    logging.warning(f"{id} current status: {issue.fields.status.name}. Must be: {str(self.complete_switch_statused[action]['from_status'])}")
                    return 255

                tr = ''
                for i in list_all_aviable_trans:
                    if action == i['name']:
                        tr = i['id']

                if not tr:
                    logging.info(f"{id} issue status: {issue.fields.status.name}. Actual trans id: {list_all_aviable_trans}")
                    raise Exception(f"Not found actual trans id for {id}")


                # нужно отправлять коммент в начале, потому что коммент в транзакции 'ответить для робота' не принимает коммент.
                with trans.start_child(op='http.client', description='transition_issue') as trans2:
                    result_trans = self.jira.transition_issue(id, transition=tr, comment=comment) # оставили коммент, чтобы был. По сути ни на что не влияет
                    trans2.set_status('ok')

                with trans.start_child(op='http', description='issue') as trans2:
                    issue = self.jira.issue(id)
                    trans2.set_status('ok')

                if issue.fields.status.name != self.complete_switch_statused[action]['new_status']:
                    logging.info(f"{id} current status: {issue.fields.status.name} result trans: {str(result_trans)}. Must be status: {self.complete_switch_statused[action]['action']}")
                    raise Exception(f"Error switch status for {id}")

                if attach:
                    try:
                        assert self.add_comments(id=id, comment='Приложены файлы', attach=attach, transaction_sentry=trans)
                    except Exception:
                        logging.exception(f"Не удалось добавить аттач в {id}")
                        return -1

                trans.set_status('ok')

        return 0
